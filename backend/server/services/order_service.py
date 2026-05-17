"""
Order Service for Go Postal SD Application

This service handles order creation, payment processing, and order management
for completed cart checkouts.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from server.config import database as db
from server.models.pricing import Cart, CartItem, ShippingOption
from server.models.order import Order, OrderItem, Payment, OrderStatus, PaymentStatus
from server.services.payment_service import PaymentService
from server.services.email_service import EmailService

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
            
            # Ensure we associate the order with the authenticated user if available
            if user_id is None and cart.user_id:
                user_id = cart.user_id
            elif user_id and not cart.user_id:
                cart.user_id = user_id

            # Generate order number
            order_number = self._generate_order_number()
            
            # Calculate totals (convert to float to avoid Decimal/float mixing)
            subtotal = sum(float(item.total_price) for item in cart.items)
            shipping_cost = self._get_shipping_cost(cart)
            tax_amount = self._calculate_tax(subtotal, cart.store_code)
            total_amount = subtotal + shipping_cost + tax_amount
            
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
            
            db.session.commit()
            
            logger.info(f"Created order {order_number} with {len(cart.items)} items")

            # Send confirmation email to customer
            self._send_order_confirmation_email(order)

            # Clear cart contents after successful order creation
            self._clear_cart(cart)
            
            return {
                'success': True,
                'order': order.to_dict(),
                'message': 'Order created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to create order: {str(e)}'
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
        try:
            # Get order
            order = Order.query.get(order_id)
            if not order:
                return {
                    'success': False,
                    'error': 'Order not found'
                }
            
            if order.payment_status != PaymentStatus.PENDING:
                return {
                    'success': False,
                    'error': 'Order payment already processed'
                }
            
            # Process payment
            payment_result = self.payment_service.process_payment(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency=order.currency,
                source_id=payment_data['source_id'],
                idempotency_key=f"order_{order.order_number}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                buyer_email=order.customer_email,
                buyer_phone=order.customer_phone,
                shipping_address=order.shipping_address,
                billing_address=order.billing_address,
                order_id=order.order_number,
                note=f"Order {order.order_number} payment"
            )
            
            if payment_result['success']:
                # Update order status
                order.payment_status = PaymentStatus.COMPLETED
                order.status = OrderStatus.PROCESSING
                
                # Create payment record (only if we have a payment_id)
                payment = None
                if payment_result.get('payment_id'):
                    payment = Payment(
                        order_id=order.id,
                        payment_provider=self.payment_service.provider,
                        external_payment_id=payment_result['payment_id'],
                        amount=order.total_amount,
                        currency=order.currency,
                        status=PaymentStatus.COMPLETED,
                        payment_method=payment_data.get('payment_method', 'card'),
                        provider_response=payment_result
                    )
                    db.session.add(payment)
                
                db.session.commit()
                
                logger.info(f"Payment processed successfully for order {order.order_number}")
                
                return {
                    'success': True,
                    'payment': payment.to_dict() if payment else {'status': 'completed'},
                    'order': order.to_dict(),
                    'message': 'Payment processed successfully'
                }
            else:
                # Payment failed - don't create a payment record if external_payment_id would be None
                order.payment_status = PaymentStatus.FAILED
                db.session.commit()
                
                logger.error(f"Payment failed for order {order.order_number}: {payment_result['error']}")
                
                return {
                    'success': False,
                    'error': payment_result['error']
                }
                
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to process payment: {str(e)}'
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
            
            # Check access (user can only see their own orders unless admin)
            if user_id and order.user_id != user_id:
                return {
                    'success': False,
                    'error': 'Access denied'
                }
            
            return {
                'success': True,
                'order': order.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting order: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get order: {str(e)}'
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
            
        except Exception as e:
            logger.error(f"Error getting user orders: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get user orders: {str(e)}'
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
                order.shipped_at = datetime.utcnow()
            elif status == OrderStatus.DELIVERED:
                order.delivered_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Updated order {order.order_number} status to {status.value}")
            
            return {
                'success': True,
                'order': order.to_dict(),
                'message': 'Order status updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to update order status: {str(e)}'
            }
    
    def _generate_order_number(self) -> str:
        """Generate unique order number."""
        timestamp = datetime.utcnow().strftime('%Y%m%d')
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
        except Exception:
            return 5.00
    
    def _calculate_tax(self, subtotal: float, store_code: int) -> float:
        """Calculate tax amount."""
        try:
            # Simple tax calculation - can be enhanced with proper tax service
            if store_code == 6:  # Canada
                return subtotal * 0.13  # 13% HST
            elif store_code == 9:  # US
                return subtotal * 0.08  # 8% average
            return 0.0
        except Exception:
            return 0.0
    
    def _send_order_confirmation_email(self, order: Order):
        """Send order confirmation email."""
        try:
            if not self.email_service or not self.email_service.is_configured:
                logger.info("Email service not configured; skipping order confirmation email")
                return

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

            subject = f"Go Postal SD Order Confirmation - {order.order_number}"
            text_content = f"""
Hello {order.customer_first_name},

Thank you for your order with Go Postal SD! Your order has been received and is now being processed.

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

If you have any questions, simply reply to this email or call us at (619) 237-0374.

Thank you,
Go Postal SD Team
            """.strip()

            items_html = "".join([
                f"<tr><td style=\"padding:6px 12px;border:1px solid #ddd;\">{item.quantity}</td>"
                f"<td style=\"padding:6px 12px;border:1px solid #ddd;\">{item.product_name}</td>"
                f"<td style=\"padding:6px 12px;border:1px solid #ddd;\">{item.product_sku or 'N/A'}</td>"
                f"<td style=\"padding:6px 12px;border:1px solid #ddd;\">${float(item.total_price):.2f}</td></tr>"
                for item in order.items
            ])

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
        <h1>Thanks for your order, {order.customer_first_name}!</h1>
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
          <p>{format_address(shipping_address).replace('\n', '<br>')}</p>
        </div>
        <div class="address">
          <h3>Billing Address</h3>
          <p>{format_address(billing_address).replace('\n', '<br>')}</p>
        </div>
      </div>
      <div class="footer">
        <p>We'll send another update once your package ships. If you have any questions, simply reply to this email or call us at (619) 237-0374.</p>
        <p>Go Postal SD<br>
           1501 India St Suite 103<br>
           San Diego, CA 92101</p>
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
            else:
                logger.info(f"Sent confirmation email for order {order.order_number} to {order.customer_email}")
            
        except Exception as e:
            logger.error(f"Error sending order confirmation email: {str(e)}")

    def _clear_cart(self, cart: Cart):
        """Remove all items and shipping selections from the cart after checkout."""
        if not cart:
            return

        try:
            CartItem.query.filter_by(cart_id=cart.id).delete()
            ShippingOption.query.filter_by(cart_id=cart.id).delete()

            # Optionally retain cart record for analytics but mark as updated
            cart.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"Cleared cart {cart.id} after order completion")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error clearing cart {cart.id if cart else 'unknown'}: {str(e)}")
