"""
Service Factory for creating all service instances.
"""

from typing import Optional
from server.thirdparty.sinalite import SinaliteAdapter
from server.services.pricing_service import PricingService
from server.services.cart_service import CartService
from server.factories.repository_factory import RepositoryFactory


class ServiceFactory:
    """
    Factory for creating all service instances.
    """
    
    _instance: Optional['ServiceFactory'] = None
    _pricing_service: Optional[PricingService] = None
    _cart_service: Optional[CartService] = None
    _repository_factory: Optional[RepositoryFactory] = None
    
    def __new__(cls) -> 'ServiceFactory':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _get_repository_factory(self) -> RepositoryFactory:
        """Get repository factory instance."""
        if self._repository_factory is None:
            self._repository_factory = RepositoryFactory()
        return self._repository_factory
    
    def get_pricing_service(self, sinalite_adapter: SinaliteAdapter) -> PricingService:
        """Get or create pricing service instance."""
        if self._pricing_service is None:
            repository_factory = self._get_repository_factory()
            self._pricing_service = PricingService(
                sinalite_adapter, 
                repository_factory.get_pricing_repository()
            )
        return self._pricing_service
    
    def get_cart_service(self, pricing_service: PricingService) -> CartService:
        """Get or create cart service instance."""
        if self._cart_service is None:
            repository_factory = self._get_repository_factory()
            self._cart_service = CartService(
                pricing_service, 
                repository_factory.get_cart_repository()
            )
        return self._cart_service
    
    def reset(self) -> None:
        """Reset all service instances (useful for testing)."""
        self._pricing_service = None
        self._cart_service = None
        if self._repository_factory:
            self._repository_factory.reset()
        self._repository_factory = None