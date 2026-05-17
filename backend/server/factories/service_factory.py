"""
Service Factory for creating all service instances.
"""

from typing import Optional
from server.thirdparty.sinalite import SinaliteAdapter
from server.services.pricing_service import PricingService
from server.services.cart_service import CartService
from server.services.auth_service import AuthService
from server.services.email_service import EmailService
from server.services.password_service import PasswordService
from server.services.role_service import RoleService
from server.factories.repository_factory import RepositoryFactory


class ServiceFactory:
    """
    Factory for creating all service instances.
    """
    
    _instance: Optional['ServiceFactory'] = None
    _pricing_service: Optional[PricingService] = None
    _cart_service: Optional[CartService] = None
    _email_service: Optional[EmailService] = None
    _password_service: Optional[PasswordService] = None
    _role_service: Optional[RoleService] = None
    _auth_service: Optional[AuthService] = None
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
    
    def get_cart_service(self, pricing_service: PricingService, sinalite_adapter: SinaliteAdapter) -> CartService:
        """Get or create cart service instance."""
        if self._cart_service is None:
            self._cart_service = CartService(pricing_service, sinalite_adapter)
        return self._cart_service
    
    def get_email_service(self) -> EmailService:
        """Get or create email service instance."""
        if self._email_service is None:
            self._email_service = EmailService()
        return self._email_service
    
    def get_password_service(self) -> PasswordService:
        """Get or create password service instance."""
        if self._password_service is None:
            self._password_service = PasswordService()
        return self._password_service
    
    def get_role_service(self) -> RoleService:
        """Get or create role service instance."""
        if self._role_service is None:
            self._role_service = RoleService()
        return self._role_service
    
    def get_auth_service(self) -> AuthService:
        """Get or create auth service instance."""
        if self._auth_service is None:
            self._auth_service = AuthService(
                self.get_email_service(),
                self.get_password_service()
            )
        return self._auth_service
    
    def reset(self) -> None:
        """Reset all service instances (useful for testing)."""
        self._pricing_service = None
        self._cart_service = None
        self._email_service = None
        self._password_service = None
        self._role_service = None
        self._auth_service = None
        if self._repository_factory:
            self._repository_factory.reset()
        self._repository_factory = None