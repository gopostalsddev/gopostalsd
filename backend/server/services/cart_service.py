"""
Cart Service for Go Postal SD Application

This module contains the business logic for shopping cart operations.
"""

from typing import Optional, List, Dict
from datetime import datetime
from server.config import database as db
from server.models.pricing import Cart, CartItem
from server.repositories.cart_repository import CartRepository
from server.services.pricing_service import PricingService
from server.models.pricing import StoreCode
import logging

logger = logging.getLogger(__name__)


class CartService:
    """
    Service for managing shopping cart operations.
    Implements the Repository pattern for data access.
    """
    
    def __init__(self, pricing_service: PricingService, repository: CartRepository):
        self.pricing_service = pricing_service
        self.repository = repository
    
    def get_or_create_cart(self, session_id: str, user_id: Optional[int] = None, 
                          store_code: int = StoreCode.CANADA.value) -> Cart:
        """
        Get existing cart or create a new one.
        
        Args:
            session_id: Session identifier
            user_id: Optional user ID for logged-in users
            store_code: Store code (6 for Canada, 9 for US)
            
        Returns:
            Cart instance
        """
        return self.repository.get_or_create_cart(session_id, user_id, store_code)
    
    def add_item_to_cart(self, cart_id: int, product_id: int, product_name: str,
                        product_sku: str, selected_options: List[int], 
                        quantity: int = 1) -> Optional[CartItem]:
        """
        Add item to cart with pricing calculation.
        
        Args:
            cart_id: Cart ID
            product_id: Sinalite product ID
            product_name: Product name
            product_sku: Product SKU
            selected_options: List of selected option IDs
            quantity: Quantity to add
            
        Returns:
            CartItem instance or None if failed
        """
        try:
            cart = self.repository.get_cart_by_id(cart_id)
            if not cart:
                logger.error(f"Cart {cart_id} not found")
                return None
            
            # Calculate price
            pricing = self.pricing_service.calculate_product_price(
                product_id, selected_options, cart.store_code
            )
            
            if not pricing:
                logger.error(f"Could not calculate price for product {product_id}")
                return None
            
            # Create option key
            option_key = "-".join(map(str, sorted(selected_options)))
            
            # Check if item already exists
            existing_item = CartItem.query.filter_by(
                cart_id=cart_id,
                product_id=product_id,
                option_key=option_key
            ).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity += quantity
                existing_item.total_price = existing_item.quantity * existing_item.unit_price
                existing_item.updated_at = datetime.utcnow()
                if self.repository.update_cart_item(existing_item):
                    return existing_item
                return None
            
            # Create new cart item
            unit_price = float(pricing.get('price', 0))
            total_price = unit_price * quantity
            
            cart_item = CartItem(
                cart_id=cart_id,
                product_id=product_id,
                product_name=product_name,
                product_sku=product_sku,
                quantity=quantity,
                selected_options=selected_options,
                option_key=option_key,
                unit_price=unit_price,
                total_price=total_price,
                package_info=pricing.get('packageInfo')
            )
            
            if self.repository.add_cart_item(cart_item):
                logger.info(f"Added item to cart {cart_id}: {product_name}")
                return cart_item
            return None
            
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            db.session.rollback()
            return None
    
    def update_cart_item_quantity(self, cart_item_id: int, quantity: int) -> bool:
        """
        Update quantity of a cart item.
        
        Args:
            cart_item_id: Cart item ID
            quantity: New quantity
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cart_item = self.repository.get_cart_item_by_id(cart_item_id)
            if not cart_item:
                logger.error(f"Cart item {cart_item_id} not found")
                return False
            
            cart_item.quantity = quantity
            cart_item.total_price = cart_item.quantity * cart_item.unit_price
            
            if self.repository.update_cart_item(cart_item):
                logger.info(f"Updated cart item {cart_item_id} quantity to {quantity}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating cart item quantity: {str(e)}")
            return False
    
    def remove_cart_item(self, cart_item_id: int) -> bool:
        """
        Remove item from cart.
        
        Args:
            cart_item_id: Cart item ID
            
        Returns:
            True if successful, False otherwise
        """
        return self.repository.delete_cart_item(cart_item_id)
    
    def get_cart_totals(self, cart_id: int) -> Dict[str, float]:
        """
        Calculate cart total including subtotal and tax.
        
        Args:
            cart_id: Cart ID
            
        Returns:
            Dict with subtotal, tax, and total amounts
        """
        try:
            cart_items = self.repository.get_cart_items(cart_id)
            
            subtotal = sum(item.total_price for item in cart_items)
            # TODO: Implement tax calculation based on location
            tax = 0.0  # Placeholder for tax calculation
            total = subtotal + tax
            
            return {
                'subtotal': float(subtotal),
                'tax': float(tax),
                'total': float(total),
                'item_count': len(cart_items)
            }
            
        except Exception as e:
            logger.error(f"Error calculating cart total: {str(e)}")
            return {'subtotal': 0.0, 'tax': 0.0, 'total': 0.0, 'item_count': 0}
