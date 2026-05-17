"""
Role Service for Go Postal SD Application

This module handles role and permission management for the authentication system.
"""

import logging
from typing import List, Dict, Any, Optional
from server.config import database as db
from server.models.auth import Role, Permission

logger = logging.getLogger(__name__)


class RoleService:
    """
    Service for handling role and permission operations.
    """

    def __init__(self):
        # Don't initialize roles in constructor - do it when first accessed
        pass

    def _initialize_default_roles(self):
        """Initialize default roles and permissions if they don't exist."""
        try:
            # Check if roles already exist
            if Role.query.first():
                return

            # Create permissions
            permissions = [
                # User permissions
                {'name': 'users.create', 'description': 'Create users', 'resource': 'users', 'action': 'create'},
                {'name': 'users.read', 'description': 'Read users', 'resource': 'users', 'action': 'read'},
                {'name': 'users.update', 'description': 'Update users', 'resource': 'users', 'action': 'update'},
                {'name': 'users.delete', 'description': 'Delete users', 'resource': 'users', 'action': 'delete'},
                
                # Product permissions
                {'name': 'products.create', 'description': 'Create products', 'resource': 'products', 'action': 'create'},
                {'name': 'products.read', 'description': 'Read products', 'resource': 'products', 'action': 'read'},
                {'name': 'products.update', 'description': 'Update products', 'resource': 'products', 'action': 'update'},
                {'name': 'products.delete', 'description': 'Delete products', 'resource': 'products', 'action': 'delete'},
                
                # Order permissions
                {'name': 'orders.create', 'description': 'Create orders', 'resource': 'orders', 'action': 'create'},
                {'name': 'orders.read', 'description': 'Read orders', 'resource': 'orders', 'action': 'read'},
                {'name': 'orders.update', 'description': 'Update orders', 'resource': 'orders', 'action': 'update'},
                {'name': 'orders.delete', 'description': 'Delete orders', 'resource': 'orders', 'action': 'delete'},
                
                # Cart permissions
                {'name': 'cart.create', 'description': 'Create cart', 'resource': 'cart', 'action': 'create'},
                {'name': 'cart.read', 'description': 'Read cart', 'resource': 'cart', 'action': 'read'},
                {'name': 'cart.update', 'description': 'Update cart', 'resource': 'cart', 'action': 'update'},
                {'name': 'cart.delete', 'description': 'Delete cart', 'resource': 'cart', 'action': 'delete'},
                
                # Admin permissions
                {'name': 'admin.access', 'description': 'Access admin panel', 'resource': 'admin', 'action': 'access'},
                {'name': 'admin.settings', 'description': 'Manage system settings', 'resource': 'admin', 'action': 'settings'},
                {'name': 'admin.reports', 'description': 'View reports', 'resource': 'admin', 'action': 'reports'},
            ]

            for perm_data in permissions:
                permission = Permission(**perm_data)
                db.session.add(permission)

            # Create roles
            roles = [
                {
                    'name': 'Admin',
                    'description': 'System administrator with full access',
                    'permissions': [
                        'users.create', 'users.read', 'users.update', 'users.delete',
                        'products.create', 'products.read', 'products.update', 'products.delete',
                        'orders.create', 'orders.read', 'orders.update', 'orders.delete',
                        'cart.create', 'cart.read', 'cart.update', 'cart.delete',
                        'admin.access', 'admin.settings', 'admin.reports'
                    ],
                    'is_system_role': True
                },
                {
                    'name': 'RegisteredCustomer',
                    'description': 'Registered customer with viewing and ordering privileges',
                    'permissions': [
                        'products.read',
                        'orders.create', 'orders.read',
                        'cart.create', 'cart.read', 'cart.update', 'cart.delete'
                    ],
                    'is_system_role': True
                },
                {
                    'name': 'GuestCustomer',
                    'description': 'Guest customer for orders without login',
                    'permissions': [
                        'products.read',
                        'cart.create', 'cart.read', 'cart.update', 'cart.delete'
                    ],
                    'is_system_role': True
                }
            ]

            for role_data in roles:
                role = Role(
                    name=role_data['name'],
                    description=role_data['description'],
                    permissions=role_data['permissions'],
                    is_system_role=role_data['is_system_role']
                )
                db.session.add(role)

            db.session.commit()
            logger.info("Default roles and permissions initialized successfully")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error initializing default roles: {str(e)}")
            raise

    def get_all_roles(self) -> List[Dict[str, Any]]:
        """
        Get all roles.
        
        Returns:
            List of role dictionaries
        """
        try:
            # Initialize default roles if they don't exist
            self._initialize_default_roles()
            
            roles = Role.query.all()
            return [
                {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description,
                    'permissions': role.permissions or [],
                    'is_system_role': role.is_system_role,
                    'created_at': role.created_at.isoformat() if role.created_at else None,
                    'updated_at': role.updated_at.isoformat() if role.updated_at else None
                }
                for role in roles
            ]
        except Exception as e:
            logger.error(f"Error getting all roles: {str(e)}")
            return []

    def get_role_by_id(self, role_id: int) -> Optional[Dict[str, Any]]:
        """
        Get role by ID.
        
        Args:
            role_id: Role ID
            
        Returns:
            Role dictionary or None
        """
        try:
            # Initialize default roles if they don't exist
            self._initialize_default_roles()
            
            role = Role.query.get(role_id)
            if not role:
                return None
            
            return {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions or [],
                'is_system_role': role.is_system_role,
                'created_at': role.created_at.isoformat() if role.created_at else None,
                'updated_at': role.updated_at.isoformat() if role.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error getting role by ID: {str(e)}")
            return None

    def get_role_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get role by name.
        
        Args:
            name: Role name
            
        Returns:
            Role dictionary or None
        """
        try:
            # Initialize default roles if they don't exist
            self._initialize_default_roles()
            
            role = Role.query.filter_by(name=name).first()
            if not role:
                return None
            
            return {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'permissions': role.permissions or [],
                'is_system_role': role.is_system_role,
                'created_at': role.created_at.isoformat() if role.created_at else None,
                'updated_at': role.updated_at.isoformat() if role.updated_at else None
            }
        except Exception as e:
            logger.error(f"Error getting role by name: {str(e)}")
            return None

    def create_role(self, name: str, description: str, permissions: List[str]) -> Dict[str, Any]:
        """
        Create a new role.
        
        Args:
            name: Role name
            description: Role description
            permissions: List of permission names
            
        Returns:
            Dict containing creation result
        """
        try:
            # Check if role already exists
            existing_role = Role.query.filter_by(name=name).first()
            if existing_role:
                return {
                    'success': False,
                    'error': 'Role with this name already exists',
                    'code': 'ROLE_EXISTS'
                }

            # Validate permissions
            valid_permissions = self._validate_permissions(permissions)
            if not valid_permissions['valid']:
                return {
                    'success': False,
                    'error': 'Invalid permissions',
                    'code': 'INVALID_PERMISSIONS',
                    'details': valid_permissions['invalid_permissions']
                }

            # Create role
            role = Role(
                name=name,
                description=description,
                permissions=permissions,
                is_system_role=False
            )
            db.session.add(role)
            db.session.commit()

            return {
                'success': True,
                'role': {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description,
                    'permissions': role.permissions,
                    'is_system_role': role.is_system_role
                }
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating role: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to create role',
                'code': 'CREATION_ERROR'
            }

    def update_role(self, role_id: int, name: str = None, description: str = None, 
                   permissions: List[str] = None) -> Dict[str, Any]:
        """
        Update a role.
        
        Args:
            role_id: Role ID
            name: New role name (optional)
            description: New role description (optional)
            permissions: New permissions list (optional)
            
        Returns:
            Dict containing update result
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                return {
                    'success': False,
                    'error': 'Role not found',
                    'code': 'ROLE_NOT_FOUND'
                }

            # Check if it's a system role
            if role.is_system_role:
                return {
                    'success': False,
                    'error': 'Cannot modify system roles',
                    'code': 'SYSTEM_ROLE'
                }

            # Update fields
            if name is not None:
                # Check if new name conflicts with existing role
                existing_role = Role.query.filter_by(name=name).first()
                if existing_role and existing_role.id != role_id:
                    return {
                        'success': False,
                        'error': 'Role with this name already exists',
                        'code': 'ROLE_EXISTS'
                    }
                role.name = name

            if description is not None:
                role.description = description

            if permissions is not None:
                # Validate permissions
                valid_permissions = self._validate_permissions(permissions)
                if not valid_permissions['valid']:
                    return {
                        'success': False,
                        'error': 'Invalid permissions',
                        'code': 'INVALID_PERMISSIONS',
                        'details': valid_permissions['invalid_permissions']
                    }
                role.permissions = permissions

            db.session.commit()

            return {
                'success': True,
                'role': {
                    'id': role.id,
                    'name': role.name,
                    'description': role.description,
                    'permissions': role.permissions,
                    'is_system_role': role.is_system_role
                }
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating role: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to update role',
                'code': 'UPDATE_ERROR'
            }

    def delete_role(self, role_id: int) -> Dict[str, Any]:
        """
        Delete a role.
        
        Args:
            role_id: Role ID
            
        Returns:
            Dict containing deletion result
        """
        try:
            role = Role.query.get(role_id)
            if not role:
                return {
                    'success': False,
                    'error': 'Role not found',
                    'code': 'ROLE_NOT_FOUND'
                }

            # Check if it's a system role
            if role.is_system_role:
                return {
                    'success': False,
                    'error': 'Cannot delete system roles',
                    'code': 'SYSTEM_ROLE'
                }

            # Check if role is in use
            if role.users:
                return {
                    'success': False,
                    'error': 'Cannot delete role that is assigned to users',
                    'code': 'ROLE_IN_USE'
                }

            db.session.delete(role)
            db.session.commit()

            return {
                'success': True,
                'message': 'Role deleted successfully'
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting role: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to delete role',
                'code': 'DELETION_ERROR'
            }

    def get_all_permissions(self) -> List[Dict[str, Any]]:
        """
        Get all permissions.
        
        Returns:
            List of permission dictionaries
        """
        try:
            permissions = Permission.query.all()
            return [
                {
                    'id': perm.id,
                    'name': perm.name,
                    'description': perm.description,
                    'resource': perm.resource,
                    'action': perm.action,
                    'created_at': perm.created_at.isoformat() if perm.created_at else None
                }
                for perm in permissions
            ]
        except Exception as e:
            logger.error(f"Error getting all permissions: {str(e)}")
            return []

    def _validate_permissions(self, permissions: List[str]) -> Dict[str, Any]:
        """
        Validate that all permissions exist.
        
        Args:
            permissions: List of permission names
            
        Returns:
            Dict containing validation result
        """
        try:
            existing_permissions = {perm.name for perm in Permission.query.all()}
            invalid_permissions = [perm for perm in permissions if perm not in existing_permissions]
            
            return {
                'valid': len(invalid_permissions) == 0,
                'invalid_permissions': invalid_permissions
            }
        except Exception as e:
            logger.error(f"Error validating permissions: {str(e)}")
            return {
                'valid': False,
                'invalid_permissions': permissions
            }
