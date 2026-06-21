# Admin User Setup Guide

## Admin User Created Successfully

Your admin user has been created and is ready for testing admin functionality.

### Admin Credentials
- **Email**: `admin@gopostalsd.com`
- **Password**: `Admin123!`
- **Role**: Admin
- **Status**: Active
- **Email Verified**: Yes

### Admin Permissions
The admin user has full access to:
- **User Management**: Create, read, update, delete users
- **Product Management**: Create, read, update, delete products  
- **Order Management**: Create, read, update, delete orders
- **Cart Management**: Full cart access
- **Admin Functions**: Access admin panel, manage settings, view reports

## How to Use

### 1. Login via API
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@gopostalsd.com",
    "password": "Admin123!"
  }'
```

### 2. Login via Frontend
Use the login form with the admin credentials above.

### 3. Test Admin Routes
Admin-protected routes use the `@require_role('Admin')` decorator:
```python
@require_role('Admin')
def admin_only_function():
    # This function requires admin role
    pass
```

## Alternative Methods

### Method 1: Use the Script (Recommended)
```bash
cd backend
python utility_scripts/create_admin_user.py
```

### Method 2: Simple Script
```bash
cd backend  
python utility_scripts/create_simple_admin.py
```

### Method 3: Manual Database Creation
If you prefer to create the admin user manually:

1. **Ensure roles exist**:
   ```python
   from server.services.role_service import RoleService
   role_service = RoleService()
   role_service._initialize_default_roles()
   ```

2. **Create admin user**:
   ```python
   from server.models.auth import User, Role, UserStatus
   from server.services.password_service import PasswordService
   
   # Get admin role
   admin_role = Role.query.filter_by(name='Admin').first()
   
   # Create user
   password_service = PasswordService()
   admin_user = User(
       first_name="Admin",
       last_name="User",
       email="admin@gopostalsd.com", 
       password_hash=password_service.hash_password("Admin123!"),
       status=UserStatus.ACTIVE,
       email_verified=True,
       role_id=admin_role.id
   )
   ```

## Verification

### Check Admin User Exists
```python
from server import create_server
from server.models.auth import User

app = create_server()
with app.app_context():
    admin = User.query.filter_by(email='admin@gopostalsd.com').first()
    if admin:
        print(f"Admin found: {admin.email} - Role: {admin.role.name}")
    else:
        print("Admin user not found")
```

### Check Admin Permissions
```python
from server.models.auth import User, Role

admin_role = Role.query.filter_by(name='Admin').first()
print("Admin permissions:")
for permission in admin_role.permissions:
    print(f"  - {permission}")
```

## Customization

### Change Admin Email
Edit the script and change:
```python
admin_email = "your-admin@yourdomain.com"
```

### Change Admin Password
Edit the script and change:
```python
admin_password = "YourSecurePassword123!"
```

### Add Multiple Admin Users
Run the script multiple times with different emails, or modify it to create multiple users.

## Security Notes

1. **Change Default Password**: The default password `Admin123!` should be changed in production
2. **Use Strong Passwords**: Ensure admin passwords meet security requirements
3. **Limit Admin Access**: Only give admin access to trusted users
4. **Monitor Admin Activity**: Log admin actions for security auditing
5. **Regular Password Updates**: Implement password rotation policies

## Troubleshooting

### "Admin role not found"
- Run database setup first: `python utility_scripts/setup_database.py`
- Ensure roles are initialized: `RoleService()._initialize_default_roles()`

### "User already exists"
- The script will detect existing admin users
- Choose to update or use existing credentials

### "Database connection error"
- Ensure database is running
- Check database configuration in environment variables
- Verify Flask app can connect to database

## Related Documentation

- [Authentication System](server-architecture.md#security-architecture)
- [API Endpoints](api-endpoints.md#authentication-endpoints-apiauth)
- [Database Models](server-architecture.md#database-models)

## Next Steps

1. **Test Login**: Use the credentials to log in
2. **Test Admin Routes**: Access admin-protected endpoints
3. **Create Additional Admins**: If needed for your team
4. **Implement Admin UI**: Build admin interface in frontend
5. **Add Admin Features**: Implement admin-specific functionality

---

**Script Location**: `backend/utility_scripts/create_admin_user.py`  
**Backup Script**: `backend/utility_scripts/create_simple_admin.py`
