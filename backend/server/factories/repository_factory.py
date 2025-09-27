"""
Repository Factory for creating all repository instances.
"""

from typing import Optional
from server.repositories.pricing_repository import PricingRepository
from server.repositories.cart_repository import CartRepository


class RepositoryFactory:
    """
    Factory for creating all repository instances.
    """
    
    _instance: Optional['RepositoryFactory'] = None
    _pricing_repository: Optional[PricingRepository] = None
    _cart_repository: Optional[CartRepository] = None
    
    def __new__(cls) -> 'RepositoryFactory':
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
    
    def reset(self) -> None:
        """Reset all repository instances (useful for testing)."""
        self._pricing_repository = None
        self._cart_repository = None
