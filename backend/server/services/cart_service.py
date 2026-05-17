"""
Cart Service for Go Postal SD Application

This service provides comprehensive cart management functionality including
adding items, updating quantities, calculating totals, and managing shipping.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from server.config import database as db
from server.models.pricing import Cart, CartItem, ShippingOption, StoreCode, ProductOption
from server.models.order import Order, OrderItem, Payment, OrderStatus, PaymentStatus
from server.models.print_product import PrintProduct
from server.services.pricing_service import PricingService
from server.thirdparty.sinalite import SinaliteAdapter

logger = logging.getLogger(__name__)

# Module load logging
IS_DEVELOPMENT = os.getenv('ENVIRONMENT', 'development') in ['development', 'testing']
if IS_DEVELOPMENT:
    logger.debug("[CART_SERVICE] Module loaded")


class CartService:
    """
    Service for handling cart operations.
    
    This service provides methods for managing shopping carts, including
    adding/removing items, calculating totals, and processing checkouts.
    """
    
    def __init__(self, pricing_service: PricingService, sinalite_adapter: SinaliteAdapter):
        self.pricing_service = pricing_service
        self.sinalite_adapter = sinalite_adapter
    
    def get_or_create_cart(self, session_id: str, user_id: Optional[int] = None) -> Cart:
        """
        Get existing cart or create a new one.
        
        Args:
            session_id: Session identifier
            user_id: Optional user ID for logged-in users
            
        Returns:
            Cart object
        """
        try:
            # Try to find existing cart
            cart = Cart.query.filter_by(session_id=session_id).first()
            
            if not cart:
                # Create new cart
                cart = Cart(
                    session_id=session_id,
                    user_id=user_id,
                    store_code=StoreCode.CANADA.value  # Default to Canada
                )
                db.session.add(cart)
                db.session.commit()
                logger.info(f"Created new cart for session {session_id}")
            else:
                # Update user_id if user logged in
                if user_id and not cart.user_id:
                    cart.user_id = user_id
                    db.session.commit()
                    logger.info(f"Associated cart {cart.id} with user {user_id}")
            
            return cart
            
        except Exception as e:
            logger.error(f"Error getting/creating cart: {str(e)}")
            db.session.rollback()
            raise
    
    def add_item_to_cart(self, 
                        session_id: str, 
                        product_id: int, 
                        selected_options: Dict[str, Any],
                        quantity: int = 1,
                        user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Add item to cart with pricing calculation.
        
        Args:
            session_id: Session identifier
            product_id: Sinalite product ID
            selected_options: Selected product options
            quantity: Quantity to add
            user_id: Optional user ID
            
        Returns:
            Dict containing operation result
        """
        try:
            logger.info(f"Adding product {product_id} to cart for session {session_id}")
            
            # Get or create cart
            cart = self.get_or_create_cart(session_id, user_id)
            
            # Get product details from our database
            if IS_DEVELOPMENT:
                logger.debug("[CART_SERVICE] Looking up product %s in database", product_id)
            
            product = PrintProduct.query.filter_by(vendor_product_id=str(product_id)).first()
            
            if not product:
                logger.error(f"Product {product_id} not found in database (vendor_product_id search)")
                if IS_DEVELOPMENT:
                    logger.debug("[CART_SERVICE] Product not found. Listing up to 5 products for debugging")
                    all_products = PrintProduct.query.limit(5).all()
                    for p in all_products:
                        logger.debug("  - Product: %s, vendor_product_id: %s, name: %s", p.id, p.vendor_product_id, p.name)
                return {
                    'success': False,
                    'error': 'Product not found'
                }
            
            if IS_DEVELOPMENT:
                logger.debug("[CART_SERVICE] Found product: %s, SKU: %s", product.name, product.sku)
            
            product_name = product.name
            product_sku = product.sku
            
            # Verify product exists in Sinalite (for pricing)
            # We don't actually need the product details from Sinalite, just verify it exists
            # The pricing service will handle the Sinalite API calls
            
            # Calculate pricing
            pricing_data = self.pricing_service.calculate_product_price(
                product_id=product_id,
                options=selected_options,  # Already a list of option IDs
                store_code=cart.store_code
            )
            
            if not pricing_data:
                error_msg = "Pricing calculation failed: No price data returned"
                logger.error(f"Pricing calculation failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # Generate option key from selected options
            option_key = "-".join(map(str, sorted(selected_options)))
            
            # Check if item already exists in cart
            existing_item = CartItem.query.filter_by(
                cart_id=cart.id,
                product_id=product_id,
                option_key=option_key
            ).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity += quantity
                existing_item.total_price = existing_item.quantity * existing_item.unit_price
                existing_item.updated_at = datetime.utcnow()
                logger.info(f"Updated quantity for existing cart item {existing_item.id}")
            else:
                # Create new cart item
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product_id,
                    product_name=product_name,
                    product_sku=product_sku,
                    quantity=quantity,
                    selected_options=selected_options,
                    option_key=option_key,
                    unit_price=pricing_data.get('price', 0),
                    total_price=pricing_data.get('price', 0) * quantity,
                    package_info=pricing_data.get('packageInfo', {})
                )
                db.session.add(cart_item)
                logger.info(f"Added new item to cart {cart.id}")
            
            db.session.commit()
            
            # Return updated cart
            return {
                'success': True,
                'cart': cart.to_dict(),
                'message': 'Item added to cart successfully'
            }
            
        except Exception as e:
            logger.error(f"Exception adding item to cart: {type(e).__name__}: {str(e)}", exc_info=True)
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to add item to cart: {str(e)}'
            }
    
    def update_cart_item_quantity(self, 
                                 session_id: str, 
                                 cart_item_id: int, 
                                 quantity: int) -> Dict[str, Any]:
        """
        Update cart item quantity.
        
        Args:
            session_id: Session identifier
            cart_item_id: Cart item ID
            quantity: New quantity
            
        Returns:
            Dict containing operation result
        """
        try:
            cart = Cart.query.filter_by(session_id=session_id).first()
            if not cart:
                return {
                    'success': False,
                    'error': 'Cart not found'
                }
            
            cart_item = CartItem.query.filter_by(
                id=cart_item_id,
                cart_id=cart.id
            ).first()
            
            if not cart_item:
                return {
                    'success': False,
                    'error': 'Cart item not found'
                }
            
            if quantity <= 0:
                # Remove item if quantity is 0 or negative
                db.session.delete(cart_item)
                logger.info(f"Removed cart item {cart_item_id}")
            else:
                # Update quantity
                cart_item.quantity = quantity
                cart_item.total_price = cart_item.quantity * cart_item.unit_price
                cart_item.updated_at = datetime.utcnow()
                logger.info(f"Updated quantity for cart item {cart_item_id}")
            
            db.session.commit()
            
            return {
                'success': True,
                'cart': cart.to_dict(),
                'message': 'Cart item updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating cart item quantity: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to update cart item: {str(e)}'
            }
    
    def remove_cart_item(self, session_id: str, cart_item_id: int) -> Dict[str, Any]:
        """
        Remove item from cart.
        
        Args:
            session_id: Session identifier
            cart_item_id: Cart item ID
            
        Returns:
            Dict containing operation result
        """
        try:
            cart = Cart.query.filter_by(session_id=session_id).first()
            if not cart:
                return {
                    'success': False,
                    'error': 'Cart not found'
                }
            
            cart_item = CartItem.query.filter_by(
                id=cart_item_id,
                cart_id=cart.id
            ).first()
            
            if not cart_item:
                return {
                    'success': False,
                    'error': 'Cart item not found'
                }
            
            db.session.delete(cart_item)
            db.session.commit()
            
            logger.info(f"Removed cart item {cart_item_id}")
            
            return {
                'success': True,
                'cart': cart.to_dict(),
                'message': 'Item removed from cart successfully'
            }
            
        except Exception as e:
            logger.error(f"Error removing cart item: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to remove cart item: {str(e)}'
            }
    
    def get_cart(self, session_id: str) -> Dict[str, Any]:
        """
        Get cart with items and totals.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict containing cart data
        """
        try:
            cart = Cart.query.filter_by(session_id=session_id).first()
            if not cart:
                return {
                    'success': True,
                    'cart': {
                        'id': None,
                        'items': [],
                        'subtotal': 0,
                        'shipping_cost': 0,
                        'tax_amount': 0,
                        'total': 0,
                        'item_count': 0
                    }
                }
            
            # Calculate totals - convert all to float to avoid Decimal/float mixing
            subtotal = sum(float(item.total_price) for item in cart.items)
            # Use constant $5 shipping fee for now
            shipping_cost = 5.00
            tax_amount = self._calculate_tax(subtotal, cart.store_code)
            total = subtotal + shipping_cost + tax_amount
            
            if IS_DEVELOPMENT:
                logger.debug(
                    "[CART_SERVICE] Cart totals: subtotal=%s, shipping=%s, tax=%s, total=%s",
                    subtotal,
                    shipping_cost,
                    tax_amount,
                    total,
                )
                for item in cart.items:
                    logger.debug(
                        "[CART_SERVICE] Item: %s, unit_price=%s, total_price=%s, qty=%s",
                        item.product_name,
                        item.unit_price,
                        item.total_price,
                        item.quantity,
                    )
            
            cart_data = cart.to_dict()
            cart_data.update({
                'subtotal': float(subtotal),
                'shipping_cost': float(shipping_cost),
                'tax_amount': float(tax_amount),
                'total': float(total),
                'item_count': len(cart.items)
            })
            
            return {
                'success': True,
                'cart': cart_data
            }
            
        except Exception as e:
            logger.error(f"Error getting cart: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get cart: {str(e)}'
            }
    
    def clear_cart(self, session_id: str) -> Dict[str, Any]:
        """
        Clear all items from cart.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict containing operation result
        """
        try:
            cart = Cart.query.filter_by(session_id=session_id).first()
            if not cart:
                return {
                    'success': False,
                    'error': 'Cart not found'
                }
            
            # Delete all cart items
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
            
            logger.info(f"Cleared cart {cart.id}")
            
            return {
                'success': True,
                'message': 'Cart cleared successfully'
            }
            
        except Exception as e:
            logger.error(f"Error clearing cart: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': f'Failed to clear cart: {str(e)}'
            }
    
    def calculate_shipping(self, 
                          session_id: str, 
                          destination_address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate shipping options for cart.
        
        NOTE: Currently using constant $5 shipping fee.
        This method is disabled to avoid Sinalite API issues.
        
        Args:
            session_id: Session identifier
            destination_address: Destination address information
            
        Returns:
            Dict containing shipping options
        """
        # Return constant shipping option for now
        return {
            'success': True,
            'shipping_options': [{
                'id': 1,
                'carrier_name': 'Standard',
                'method_name': 'Standard Shipping',
                'price': 5.00,
                'shipping_days': 7,
                'destination_state': destination_address.get('state', ''),
                'destination_zip': destination_address.get('zip', '') or destination_address.get('zip_code', ''),
                'destination_country': destination_address.get('country', 'CA')
            }]
        }
    
    def _calculate_shipping_cost(self, cart: Cart) -> float:
        """Calculate shipping cost for cart."""
        # Using constant $5 shipping fee for now
        return 5.00
    
    def _calculate_tax(self, subtotal: float, store_code: int) -> float:
        """Calculate tax amount."""
        try:
            # Simple tax calculation - can be enhanced with proper tax service
            if store_code == StoreCode.CANADA.value:
                # Canadian tax rate (simplified)
                return subtotal * 0.13  # 13% HST
            elif store_code == StoreCode.US.value:
                # US tax rate (simplified)
                return subtotal * 0.08  # 8% average
            return 0.0
        except Exception:
            return 0.0