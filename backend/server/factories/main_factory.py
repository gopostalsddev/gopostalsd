"""
Main Factory for coordinating all factories.
Implements the Facade pattern for clean service instantiation.
"""

from typing import Optional
from server.thirdparty.sinalite import SinaliteAdapter
from server.services.pricing_service import PricingService
from server.services.cart_service import CartService
from server.factories.repository_factory import RepositoryFactory
from server.factories.service_factory import ServiceFactory
from server.factories.controller_factory import ControllerFactory


class MainFactory:
    """
    Main factory for coordinating all other factories.
    Implements the Facade pattern for clean service instantiation.
    """
    
    _instance: Optional['MainFactory'] = None
    _repository_factory: Optional[RepositoryFactory] = None
    _service_factory: Optional[ServiceFactory] = None
    _controller_factory: Optional[ControllerFactory] = None
    
    def __new__(cls) -> 'MainFactory':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _get_repository_factory(self) -> RepositoryFactory:
        """Get repository factory instance."""
        if self._repository_factory is None:
            self._repository_factory = RepositoryFactory()
        return self._repository_factory
    
    def _get_service_factory(self) -> ServiceFactory:
        """Get service factory instance."""
        if self._service_factory is None:
            self._service_factory = ServiceFactory()
        return self._service_factory
    
    def _get_controller_factory(self) -> ControllerFactory:
        """Get controller factory instance."""
        if self._controller_factory is None:
            self._controller_factory = ControllerFactory()
        return self._controller_factory
    
    # Repository access methods
    def get_pricing_repository(self):
        """Get pricing repository instance."""
        return self._get_repository_factory().get_pricing_repository()
    
    def get_cart_repository(self):
        """Get cart repository instance."""
        return self._get_repository_factory().get_cart_repository()
    
    # Service access methods
    def get_pricing_service(self, sinalite_adapter: SinaliteAdapter) -> PricingService:
        """Get pricing service instance."""
        return self._get_service_factory().get_pricing_service(sinalite_adapter)
    
    def get_cart_service(self, pricing_service: PricingService, sinalite_adapter: SinaliteAdapter) -> CartService:
        """Get cart service instance."""
        return self._get_service_factory().get_cart_service(pricing_service, sinalite_adapter)
    
    def get_email_service(self):
        """Get email service instance."""
        return self._get_service_factory().get_email_service()
    
    def get_password_service(self):
        """Get password service instance."""
        return self._get_service_factory().get_password_service()
    
    def get_role_service(self):
        """Get role service instance."""
        return self._get_service_factory().get_role_service()
    
    def get_auth_service(self):
        """Get auth service instance."""
        return self._get_service_factory().get_auth_service()
    
    # Controller access methods
    def get_pricing_controller(self):
        """Get pricing controller class."""
        return self._get_controller_factory().get_pricing_controller()
    
    def get_print_product_controller(self):
        """Get print product controller class."""
        return self._get_controller_factory().get_print_product_controller()
    
    def get_user_controller(self):
        """Get user controller class."""
        return self._get_controller_factory().get_user_controller()
    
    def get_cart_controller(self):
        """Get cart controller class."""
        return self._get_controller_factory().get_cart_controller()
    
    def get_auth_controller(self):
        """Get auth controller class."""
        return self._get_controller_factory().get_auth_controller()
    
    def reset(self) -> None:
        """Reset all instances (useful for testing)."""
        if self._repository_factory:
            self._repository_factory.reset()
        if self._service_factory:
            self._service_factory.reset()
        if self._controller_factory:
            self._controller_factory.reset()
        self._repository_factory = None
        self._service_factory = None
        self._controller_factory = None
