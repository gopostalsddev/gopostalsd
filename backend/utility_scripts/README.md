# Utility Scripts

This directory contains utility scripts for managing the Go Postal SD backend.

## Available Scripts

### Database Setup
- **`setup_database.py`** - Initialize database with all tables and initial data
- **`verify_tables.py`** - Verify that all required database tables exist

### User Management
- **`create_admin_user.py`** - Create an admin user account
- **`create_simple_admin.py`** - Create a simple admin user with minimal configuration
- **`create_simple_customer.py`** - Create John Doe as a RegisteredCustomer test user

### Migration Tools
- **`create_auth_migration.py`** - Create authentication migration
- **`create_order_tables.py`** - Create order-related tables

### Environment Setup
- **`setup_env.py`** - Generate `.env` file for different environments

## Production Database Setup

To create your production database from scratch and match your local setup:

### Method 1: Using setup_database.py (Recommended)

1. **Connect to your production server** and navigate to the backend directory
2. **Ensure your `.env` file is configured** with production database credentials:
   ```env
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ENVIRONMENT=production
   ```

3. **Run the setup script**:
   ```bash
   python utility_scripts/setup_database.py
   ```

This script will:
- ✅ Run all pending migrations
- ✅ Create all database tables
- ✅ Initialize required initial data (e.g., unclassified product type)
- ✅ Verify database health and table existence

### Method 2: Using Flask-Migrate commands

If you prefer to use Flask-Migrate CLI:

```bash
# Set your environment
export ENVIRONMENT=production
# or set it in .env file

# Run migrations
flask db upgrade

# Then initialize data manually if needed
python utility_scripts/create_simple_admin.py
```

### Method 3: Using the scripts/run_migrations.py

```bash
python scripts/run_migrations.py
```

## Creating Admin Users

After setting up the database, create your admin user:

```bash
# Full-featured admin user
python utility_scripts/create_admin_user.py

# Or simple admin user
python utility_scripts/create_simple_admin.py
```

## Verifying Database Setup

To verify your database is properly set up:

```bash
python utility_scripts/verify_tables.py
```

## Production Checklist

1. ✅ Set `ENVIRONMENT=production` in `.env`
2. ✅ Configure `DATABASE_URL` with production PostgreSQL credentials
3. ✅ Set other required environment variables (see `env.example`)
4. ✅ Run `python utility_scripts/setup_database.py`
5. ✅ Create admin user: `python utility_scripts/create_admin_user.py`
6. ✅ Verify setup: `python utility_scripts/verify_tables.py`
7. ✅ Start the application: `python app.py`

## Environment Variables Required

Make sure your production `.env` includes:
- `ENVIRONMENT=production`
- `DATABASE_URL` - PostgreSQL connection string
- `SINALITE_CLIENT_ID` - Sinalite API credentials
- `SINALITE_CLIENT_SECRET` - Sinalite API credentials
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `SECRET_KEY` - Flask secret key
- `SMTP_*` or MailerSend credentials
- Other third-party service credentials as needed

## Notes

- All scripts should be run from the `backend` directory
- The `setup_database.py` script is idempotent - safe to run multiple times
- Migrations are version-controlled and tracked in the `migrations/versions/` directory
- Always backup your production database before running migrations

