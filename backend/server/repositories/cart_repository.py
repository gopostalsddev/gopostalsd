"""
Cart Repository for Go Postal SD Application

This module contains all cart-related database operations.
Follows the Repository pattern for clean data access.
"""

from typing import Optional, List
from datetime import datetime, timezone
from server.config import database as db
from server.models.pricing import Cart, CartItem, StoreCode
import logging

logger = logging.getLogger(__name__)


class CartRepository:
    """
    Repository for cart-related database operations.
    Follows the Repository pattern for clean data access.
    """
    
    def get_or_create_cart(self, session_id: str, user_id: Optional[int] = None, 
                          store_code: int = StoreCode.CANADA.value) -> Cart:
        """Get existing cart or create a new one."""
        try:
            cart = Cart.query.filter_by(session_id=session_id).first()
            
            if not cart:
                cart = Cart(
                    session_id=session_id,
                    user_id=user_id,
                    store_code=store_code
                )
                db.session.add(cart)
                db.session.commit()
                logger.info(f"Created new cart for session {session_id}")
            else:
                # Update store code if different
                if cart.store_code != store_code:
                    cart.store_code = store_code
                    db.session.commit()
            
            return cart
            
        except Exception as e:
            logger.error(f"Error getting/creating cart: {str(e)}")
            db.session.rollback()
            raise
    
    def get_cart_by_id(self, cart_id: int) -> Optional[Cart]:
        """Get cart by ID."""
        try:
            return Cart.query.get(cart_id)
        except Exception as e:
            logger.error(f"Error getting cart {cart_id}: {str(e)}")
            return None
    
    def add_cart_item(self, cart_item: CartItem) -> bool:
        """Add cart item to database."""
        try:
            db.session.add(cart_item)
            db.session.commit()
            logger.info(f"Added cart item for product {cart_item.product_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding cart item: {str(e)}")
            db.session.rollback()
            return False
    
    def update_cart_item(self, cart_item: CartItem) -> bool:
        """Update cart item in database."""
        try:
            cart_item.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            logger.info(f"Updated cart item {cart_item.id}")
            return True
        except Exception as e:
            logger.error(f"Error updating cart item: {str(e)}")
            db.session.rollback()
            return False
    
    def get_cart_item_by_id(self, cart_item_id: int) -> Optional[CartItem]:
        """Get cart item by ID."""
        try:
            return CartItem.query.get(cart_item_id)
        except Exception as e:
            logger.error(f"Error getting cart item {cart_item_id}: {str(e)}")
            return None
    
    def get_cart_items(self, cart_id: int) -> List[CartItem]:
        """Get all items in a cart."""
        try:
            return CartItem.query.filter_by(cart_id=cart_id).all()
        except Exception as e:
            logger.error(f"Error getting cart items for cart {cart_id}: {str(e)}")
            return []
    
    def delete_cart_item(self, cart_item_id: int) -> bool:
        """Delete cart item from database."""
        try:
            cart_item = CartItem.query.get(cart_item_id)
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
                logger.info(f"Deleted cart item {cart_item_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting cart item {cart_item_id}: {str(e)}")
            db.session.rollback()
            return False
