"""
Service Factory for creating service instances.
Implements the Factory pattern for service instantiation.
"""

from typing import Optional
from server.thirdparty.sinalite import SinaliteAdapter
from server.services.pricing_service import PricingService, CartService
from server.repositories.pricing_repository import PricingRepository, CartRepository


class ServiceFactory:
    """
    Factory for creating service instances.
    Follows the Factory pattern for clean service instantiation.
    """
    
    _instance: Optional['ServiceFactory'] = None
    _pricing_service: Optional[PricingService] = None
    _cart_service: Optional[CartService] = None
    _pricing_repository: Optional[PricingRepository] = None
    _cart_repository: Optional[CartRepository] = None
    
    def __new__(cls) -> 'ServiceFactory':
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_pricing_repository(self) -> PricingRepository:
        """Get or create pricing repository instance."""
        if self._pricing_repository is None:
            self._pricing_repository = PricingRepository()
        return self._pricing_repository
    
    def get_cart_repository(self) -> CartRepository:
        """Get or create cart repository instance."""
        if self._cart_repository is None:
            self._cart_repository = CartRepository()
        return self._cart_repository
    
    def get_pricing_service(self, sinalite_adapter: SinaliteAdapter) -> PricingService:
        """Get or create pricing service instance."""
        if self._pricing_service is None:
            self._pricing_service = PricingService(sinalite_adapter, self.get_pricing_repository())
        return self._pricing_service
    
    def get_cart_service(self, pricing_service: PricingService) -> CartService:
        """Get or create cart service instance."""
        if self._cart_service is None:
            self._cart_service = CartService(pricing_service, self.get_cart_repository())
        return self._cart_service
    
    def reset(self) -> None:
        """Reset all service instances (useful for testing)."""
        self._pricing_service = None
        self._cart_service = None
        self._pricing_repository = None
        self._cart_repository = None
