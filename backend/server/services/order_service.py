"""
Order Service for Go Postal SD Application

This service handles order creation, payment processing, and order management
for completed cart checkouts.
"""

import logging
import hashlib
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from markupsafe import escape as html_escape
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.exc import SQLAlchemyError
from server.config import database as db
from server.models.pricing import Cart, CartItem, ShippingOption
from server.models.order import (
    Order, OrderItem, Payment, PaymentAttempt, OrderStatus, PaymentStatus,
)
from server.services.payment_service import PaymentService
from server.services.email_service import EmailService
from server.email_config import BRAND_NAME, INTENDED_SENDER_ADDRESS, PLATFORM_ATTRIBUTION

logger = logging.getLogger(__name__)


class OrderService:
    """
    Service for handling order operations.
    
    This service provides methods for creating orders from carts,
    processing payments, and managing order lifecycle.
    """
    
    def __init__(self, payment_service: PaymentService, email_service: EmailService):
        self.payment_service = payment_service
        self.email_service = email_service

    @staticmethod
    def _to_money_decimal(value: Any) -> Decimal:
        """Convert value to 2-decimal money representation."""
        return Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def create_order_from_cart(self, 
                              session_id: str,
                              customer_info: Dict[str, Any],
                              shipping_address: Dict[str, Any],
                              billing_address: Optional[Dict[str, Any]] = None,
                              user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Create order from cart items.
        
        Args:
            session_id: Session identifier
            customer_info: Customer information (email, name, phone)
            shipping_address: Shipping address
            billing_address: Billing address (optional)
            user_id: Optional user ID for logged-in users
            
        Returns:
            Dict containing order creation result
        """
        try:
            # Get cart
            cart = Cart.query.filter_by(session_id=session_id).first()
            if not cart:
                return {
                    'success': False,
                    'error': 'Cart not found'
                }
            
            if not cart.items:
                return {
                    'success': False,
                    'error': 'Cart is empty'
                }
            
            # Ownership check: an authenticated user may only checkout their own cart.
            # A guest (user_id=None) may only checkout an ownerless cart.
            if user_id is not None and cart.user_id is not None and cart.user_id != user_id:
                return {'success': False, 'error': 'Access denied'}
            if user_id is None and cart.user_id is not None:
                return {'success': False, 'error': 'Access denied'}

            # Associate the order with the authenticated user if available.
            if user_id is None and cart.user_id:
                user_id = cart.user_id
            elif user_id and not cart.user_id:
                cart.user_id = user_id

            # Generate order number
            order_number = self._generate_order_number()
            
            # Calculate totals with Decimal to preserve money precision.
            subtotal = sum((self._to_money_decimal(item.total_price) for item in cart.items), Decimal('0.00'))
            shipping_cost = self._to_money_decimal(self._get_shipping_cost(cart))
            tax_amount = self._to_money_decimal(self._calculate_tax(float(subtotal), cart.store_code))
            total_amount = self._to_money_decimal(subtotal + shipping_cost + tax_amount)
            
            # Create order
            order = Order(
                order_number=order_number,
                user_id=user_id,
                session_id=session_id,
                customer_email=customer_info['email'],
                customer_first_name=customer_info['first_name'],
                customer_last_name=customer_info['last_name'],
                customer_phone=customer_info.get('phone'),
                status=OrderStatus.PENDING,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax_amount=tax_amount,
                total_amount=total_amount,
                currency='USD',
                shipping_address=shipping_address,
                billing_address=billing_address or shipping_address,
                payment_status=PaymentStatus.PENDING
            )
            
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Create order items
            for cart_item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    product_name=cart_item.product_name,
                    product_sku=cart_item.product_sku,
                    quantity=cart_item.quantity,
                    selected_options=cart_item.selected_options,
                    option_key=cart_item.option_key,
                    unit_price=cart_item.unit_price,
                    total_price=cart_item.total_price,
                    package_info=cart_item.package_info
                )
                db.session.add(order_item)
            
            # Clear cart in the same transaction as order creation.
            self._clear_cart_in_session(cart)

            db.session.commit()
            logger.info(f"Created order {order_number} with {len(cart.items)} items")

            email_sent = self._send_order_confirmation_email(order)
            message = 'Order created successfully' if email_sent else 'Order created successfully. Confirmation email is pending.'
            
            return {
                'success': True,
                'order': order.to_dict(),
                'message': message
            }
            
        except (SQLAlchemyError, KeyError, ValueError, TypeError, InvalidOperation):
            logger.error("Error creating order", exc_info=True)
            db.session.rollback()
            return {
                'success': False,
                'error': 'Failed to create order'
            }
    
    def process_payment(self, 
                       order_id: int, 
                       payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment for an order.
        
        Args:
            order_id: Order ID
            payment_data: Payment information (source_id, etc.)
            
        Returns:
            Dict containing payment result
        """
        attempt_id = None
        try:
            source_id = payment_data['source_id']
            source_fingerprint = hashlib.sha256(source_id.encode()).hexdigest()

            # Reserve a stable provider identity while holding the order lock,
            # then commit it before any network call is made.
            order = Order.query.with_for_update().filter_by(id=order_id).first()
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }

            if order.payment_status == PaymentStatus.COMPLETED:
                payment = Payment.query.filter_by(order_id=order.id).order_by(Payment.id.desc()).first()
                if payment:
                    return {
                        'success': True,
                        'payment': payment.to_dict(),
                        'order': order.to_dict(),
                        'message': 'Payment already completed',
                    }
                return {
                    'success': False,
                    'error': 'Order payment already processed'
                }

            amount_cents = int(self._to_money_decimal(order.total_amount) * 100)
            active = (
                PaymentAttempt.query.with_for_update()
                .filter(
                    PaymentAttempt.order_id == order.id,
                    PaymentAttempt.status.in_(('reserved', 'processing', 'unknown')),
                )
                .order_by(PaymentAttempt.id.desc())
                .first()
            )

            if active:
                if (
                    active.amount_cents != amount_cents
                    or active.currency != order.currency
                    or active.source_fingerprint != source_fingerprint
                ):
                    return {
                        'success': False,
                        'error': 'A payment is already being reconciled for this order',
                    }
                if active.status == 'processing':
                    return {
                        'success': False,
                        'error': 'Payment processing is already in progress',
                    }
                attempt = active
                attempt.status = 'processing'
                attempt.last_error_code = None
            else:
                key = str(uuid.uuid4())
                attempt = PaymentAttempt(
                    order_id=order.id,
                    provider=self.payment_service.provider,
                    idempotency_key=key,
                    provider_reference=f"gp-{order.id}-{uuid.uuid4().hex[:20]}",
                    source_fingerprint=source_fingerprint,
                    amount_cents=amount_cents,
                    currency=order.currency,
                    status='processing',
                )
                db.session.add(attempt)

            order.payment_status = PaymentStatus.PROCESSING
            db.session.commit()
            attempt_id = attempt.id

            try:
                payment_result = self.payment_service.process_payment(
                    amount=attempt.amount_cents,
                    currency=order.currency,
                    source_id=source_id,
                    idempotency_key=attempt.idempotency_key,
                    buyer_email=order.customer_email,
                    buyer_phone=order.customer_phone,
                    shipping_address=order.shipping_address,
                    billing_address=order.billing_address,
                    reference_id=attempt.provider_reference,
                    note=f"Order {order.order_number} payment"
                )
            except Exception:
                logger.error("Payment provider outcome is unknown", exc_info=True)
                payment_result = {
                    'success': False,
                    'outcome_known': False,
                    'error': 'Payment provider outcome is unknown',
                }

            attempt = PaymentAttempt.query.with_for_update().filter_by(id=attempt_id).one()
            order = Order.query.with_for_update().filter_by(id=order_id).one()

            # A webhook may have completed reconciliation while the provider
            # response was in flight.
            if attempt.status == 'succeeded':
                payment = Payment.query.filter_by(
                    payment_provider=attempt.provider,
                    external_payment_id=attempt.external_payment_id,
                ).one()
                return {
                    'success': True,
                    'payment': payment.to_dict(),
                    'order': order.to_dict(),
                    'message': 'Payment processed successfully',
                }

            if payment_result['success']:
                external_id = payment_result.get('payment_id')
                if not external_id:
                    raise RuntimeError('provider success lacked payment identity')

                order.payment_status = PaymentStatus.COMPLETED
                order.status = OrderStatus.PROCESSING
                order.payment_id = external_id
                order.payment_provider = self.payment_service.provider

                payment = Payment.query.filter_by(
                    payment_provider=self.payment_service.provider,
                    external_payment_id=external_id,
                ).first()
                if not payment:
                    payment = Payment(
                        order_id=order.id,
                        payment_provider=self.payment_service.provider,
                        external_payment_id=external_id,
                        amount=order.total_amount,
                        currency=order.currency,
                        status=PaymentStatus.COMPLETED,
                        payment_method=payment_data.get('payment_method', 'card'),
                        provider_response=payment_result
                    )
                    db.session.add(payment)

                attempt.status = 'succeeded'
                attempt.external_payment_id = external_id
                attempt.provider_response = payment_result
                attempt.completed_at = datetime.now(timezone.utc)
                db.session.commit()

                logger.info(f"Payment processed successfully for order {order.order_number}")
                return {
                    'success': True,
                    'payment': payment.to_dict(),
                    'order': order.to_dict(),
                    'message': 'Payment processed successfully'
                }

            if payment_result.get('outcome_known', True):
                attempt.status = 'failed'
                attempt.last_error_code = 'provider_declined'
                attempt.provider_response = {'success': False, 'outcome_known': True}
                order.payment_status = PaymentStatus.PENDING
                db.session.commit()
                logger.warning("Payment attempt was declined for order %s", order.order_number)
                return {
                    'success': False,
                    'error': payment_result['error']
                }

            attempt.status = 'unknown'
            attempt.last_error_code = 'provider_outcome_unknown'
            attempt.provider_response = {'success': False, 'outcome_known': False}
            order.payment_status = PaymentStatus.PROCESSING
            db.session.commit()
            return {
                'success': False,
                'error': 'Payment status is being reconciled; do not submit another card',
            }

        except (SQLAlchemyError, KeyError, ValueError, TypeError, InvalidOperation, RuntimeError):
            logger.error("Error processing payment", exc_info=True)
            db.session.rollback()
            if attempt_id is not None:
                try:
                    attempt = PaymentAttempt.query.filter_by(id=attempt_id).first()
                    order = Order.query.filter_by(id=order_id).first()
                    if attempt and attempt.status != 'succeeded':
                        attempt.status = 'unknown'
                        attempt.last_error_code = 'local_reconciliation_failed'
                    if order and order.payment_status != PaymentStatus.COMPLETED:
                        order.payment_status = PaymentStatus.PROCESSING
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
            return {
                'success': False,
                'error': 'Payment status is being reconciled; do not submit another card'
            }
    
    def get_order(self, order_id: int, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get order details.
        
        Args:
            order_id: Order ID
            user_id: Optional user ID for access control
            
        Returns:
            Dict containing order data
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            # Authenticated users may only read orders that belong to their account.
            # Guest orders (order.user_id is None) are never readable by other authenticated users.
            if user_id is not None:
                if order.user_id is None or order.user_id != user_id:
                    return {
                        'success': False,
                        'error': 'Access denied'
                    }
            
            return {
                'success': True,
                'order': order.to_dict()
            }
            
        except SQLAlchemyError:
            logger.error("Error getting order", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get order'
            }
    
    def get_user_orders(self, user_id: int, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Get user's orders.
        
        Args:
            user_id: User ID
            limit: Number of orders to return
            offset: Offset for pagination
            
        Returns:
            Dict containing orders list
        """
        try:
            orders = Order.query.filter_by(user_id=user_id)\
                .order_by(Order.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()
            
            total_count = Order.query.filter_by(user_id=user_id).count()
            
            return {
                'success': True,
                'orders': [order.to_dict() for order in orders],
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except ProgrammingError as e:
            if 'relation "orders" does not exist' in str(e):
                logger.warning("Orders table missing while fetching user orders; returning empty list")
                return {
                    'success': True,
                    'orders': [],
                    'total_count': 0,
                    'limit': limit,
                    'offset': offset,
                }
            logger.error("Error getting user orders", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get user orders'
            }
        except SQLAlchemyError:
            logger.error("Error getting user orders", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get user orders'
            }

    def get_all_orders(self,
                      limit: int = 50,
                      offset: int = 0,
                      status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all orders for admin management.

        Args:
            limit: Number of orders to return
            offset: Offset for pagination
            status: Optional status filter

        Returns:
            Dict containing orders list
        """
        try:
            query = Order.query

            if status:
                try:
                    query = query.filter_by(status=OrderStatus(status))
                except ValueError:
                    return {
                        'success': False,
                        'error': 'Invalid status filter'
                    }

            orders = query.order_by(Order.created_at.desc())\
                .limit(limit)\
                .offset(offset)\
                .all()

            total_count = query.count()

            return {
                'success': True,
                'orders': [order.to_dict() for order in orders],
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }

        except SQLAlchemyError:
            logger.error("Error getting all orders", exc_info=True)
            return {
                'success': False,
                'error': 'Failed to get all orders'
            }
    
    def update_order_status(self, 
                           order_id: int, 
                           status: OrderStatus,
                           tracking_number: Optional[str] = None,
                           carrier_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Update order status (admin only).
        
        Args:
            order_id: Order ID
            status: New order status
            tracking_number: Optional tracking number
            carrier_name: Optional carrier name
            
        Returns:
            Dict containing update result
        """
        try:
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            order.status = status
            
            if tracking_number:
                order.tracking_number = tracking_number
            if carrier_name:
                order.carrier_name = carrier_name
            
            if status == OrderStatus.SHIPPED:
                order.shipped_at = datetime.now(timezone.utc)
            elif status == OrderStatus.DELIVERED:
                order.delivered_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            logger.info(f"Updated order {order.order_number} status to {status.value}")
            
            return {
                'success': True,
                'order': order.to_dict(),
                'message': 'Order status updated successfully'
            }
            
        except SQLAlchemyError:
            logger.error("Error updating order status", exc_info=True)
            db.session.rollback()
            return {
                'success': False,
                'error': 'Failed to update order status'
            }
    
    def _generate_order_number(self) -> str:
        """Generate unique order number."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"GP{timestamp}{unique_id}"
    
    def _get_shipping_cost(self, cart: Cart) -> float:
        """Get shipping cost for cart."""
        try:
            shipping_option = ShippingOption.query.filter_by(cart_id=cart.id).first()
            if shipping_option:
                return float(shipping_option.price)
            # Default to constant $5 shipping if no option selected
            return 5.00
        except (SQLAlchemyError, TypeError, ValueError):
            return 5.00
    
    def _calculate_tax(self, subtotal: float, store_code: int) -> float:
        """Calculate tax amount."""
        try:
            from server.models.pricing import StoreCode
            # Only apply known, server-defined tax rates — unrecognised codes get 0%.
            code = int(store_code)
            if code == StoreCode.CANADA.value:
                return subtotal * 0.13  # 13% HST
            elif code == StoreCode.US.value:
                return subtotal * 0.08  # 8% average
            return 0.0
        except (TypeError, ValueError):
            return 0.0
    
    def _send_order_confirmation_email(self, order: Order) -> bool:
        """Send order confirmation email."""
        try:
            if not self.email_service or not self.email_service.is_configured:
                logger.info("Email service not configured; skipping order confirmation email")
                return False

            tracking_number = order.tracking_number or "Pending - you'll receive an update once your package ships."
            shipping_address = order.shipping_address or {}
            billing_address = order.billing_address or shipping_address

            def format_address(address: Dict[str, Any]) -> str:
                parts = [
                    address.get('street'),
                    address.get('apt'),
                    f"{address.get('city')}, {address.get('state')} {address.get('zip_code')}",
                    address.get('country')
                ]
                return "\n".join([part for part in parts if part])

            items_lines = []
            for item in order.items:
                items_lines.append(f"- {item.quantity} x {item.product_name} (SKU: {item.product_sku or 'N/A'}) - ${float(item.total_price):.2f}")
            items_text = "\n".join(items_lines) if items_lines else "No items found."

            subject = f"{BRAND_NAME} Order Confirmation - {order.order_number}"
            text_content = f"""
Hello {order.customer_first_name},

Thank you for your order with {BRAND_NAME}! Your order has been received and is now being processed.

Order Number: {order.order_number}
Tracking Number: {tracking_number}
Order Total: ${float(order.total_amount):.2f} USD

Order Items:
{items_text}

Shipping Address:
{format_address(shipping_address)}

Billing Address:
{format_address(billing_address)}

We will send you another update once your package is on the way.

If you have any questions, simply reply to this email or contact {INTENDED_SENDER_ADDRESS}.

Thank you,
{BRAND_NAME} Team
{PLATFORM_ATTRIBUTION}
            """.strip()

            items_html = "".join([
                f"<tr><td style=\"padding:6px 12px;border:1px solid #ddd;\">{item.quantity}</td>"
                f"<td style=\"padding:6px 12px;border:1px solid #ddd;\">{html_escape(item.product_name)}</td>"
                f"<td style=\"padding:6px 12px;border:1px solid #ddd;\">{html_escape(item.product_sku or 'N/A')}</td>"
                f"<td style=\"padding:6px 12px;border:1px solid #ddd;\">${float(item.total_price):.2f}</td></tr>"
                for item in order.items
            ])

            shipping_html = html_escape(format_address(shipping_address)).replace("\n", "<br>")
            billing_html = html_escape(format_address(billing_address)).replace("\n", "<br>")

            html_content = f"""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Order Confirmation</title>
    <style>
      body {{ font-family: Arial, sans-serif; color: #333; }}
      .container {{ max-width: 640px; margin: 0 auto; padding: 20px; }}
      .header {{ text-align: center; margin-bottom: 24px; }}
      .summary {{ background-color: #f5f5f5; padding: 16px; border-radius: 6px; margin-bottom: 24px; }}
      .summary h2 {{ margin-top: 0; }}
      table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; }}
      th {{ background-color: #1976d2; color: white; padding: 8px 12px; text-align: left; }}
      td {{ padding: 6px 12px; border: 1px solid #ddd; }}
      .footer {{ margin-top: 32px; font-size: 14px; color: #666; }}
      .addresses {{ display: flex; flex-wrap: wrap; gap: 20px; }}
      .address {{ flex: 1 1 240px; background: #fafafa; padding: 16px; border-radius: 6px; }}
      .address h3 {{ margin-top: 0; }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="header">
        <h1>Thanks for your order, {html_escape(order.customer_first_name)}!</h1>
        <p>Your order has been received and is now being processed.</p>
      </div>
      <div class="summary">
        <h2>Order Summary</h2>
        <p><strong>Order Number:</strong> {order.order_number}<br>
           <strong>Tracking Number:</strong> {tracking_number}<br>
           <strong>Total:</strong> ${float(order.total_amount):.2f} USD</p>
      </div>
      <table>
        <thead>
          <tr>
            <th>Qty</th>
            <th>Item</th>
            <th>SKU</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {items_html or '<tr><td colspan="4" style="padding:12px; text-align:center;">No items found.</td></tr>'}
        </tbody>
      </table>
      <div class="addresses">
        <div class="address">
          <h3>Shipping Address</h3>
          <p>{shipping_html}</p>
        </div>
        <div class="address">
          <h3>Billing Address</h3>
          <p>{billing_html}</p>
        </div>
      </div>
      <div class="footer">
        <p>We'll send another update once your package ships. If you have any questions, simply reply to this email or contact {INTENDED_SENDER_ADDRESS}.</p>
        <p>{BRAND_NAME}<br>{PLATFORM_ATTRIBUTION}</p>
      </div>
    </div>
  </body>
</html>
            """.strip()

            result = self.email_service.send_email(
                to_email=order.customer_email,
                subject=subject,
                text_content=text_content,
                html_content=html_content
            )

            if not result.get('success'):
                logger.error(f"Failed to send order confirmation email: {result.get('error')}")
                return False
            else:
                logger.info(f"Sent confirmation email for order {order.order_number} to {order.customer_email}")
                return True
            
        except (AttributeError, TypeError, ValueError, RuntimeError):
            logger.error("Error sending order confirmation email", exc_info=True)
            return False

    def _clear_cart_in_session(self, cart: Cart):
        """Remove cart data using the current transaction/session."""
        if not cart:
            return

        CartItem.query.filter_by(cart_id=cart.id).delete()
        ShippingOption.query.filter_by(cart_id=cart.id).delete()
        cart.updated_at = datetime.now(timezone.utc)
