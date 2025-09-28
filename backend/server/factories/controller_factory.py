"""
Controller Factory for creating all controller instances.
Note: Controllers remain static classes, this factory just provides access to them.
"""

from typing import Optional


class ControllerFactory:
    """
    Factory for providing access to controller classes.
    Controllers remain static classes as per requirement.
    """
    
    _instance: Optional['ControllerFactory'] = None
    
    def __new__(cls) -> 'ControllerFactory':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_pricing_controller(self):
        """
        Get pricing controller class.
        Controllers are static, so we just return the class.
        """
        from server.controllers.pricing_controller import PricingController
        return PricingController
    
    def get_print_product_controller(self):
        """
        Get print product controller class.
        Controllers are static, so we just return the class.
        """
        from server.controllers.print_product_controller import PrintProductController
        return PrintProductController
    
    def get_user_controller(self):
        """
        Get user controller class.
        Controllers are static, so we just return the class.
        """
        from server.controllers.user_controller import UserController
        return UserController
    
    def get_cart_controller(self):
        """
        Get cart controller class.
        Controllers are static, so we just return the class.
        """
        from server.controllers.cart_controller import CartController
        return CartController
    
    def reset(self) -> None:
        """Reset all instances (useful for testing)."""
        pass  # No instances to reset for static controllers
