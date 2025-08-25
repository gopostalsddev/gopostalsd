# Database Scripts

This directory contains utility scripts for database management and system setup.

## Scripts

### `run_migrations.py`
**Purpose**: Run all pending database migrations  
**Usage**: `python scripts/run_migrations.py`  
**When to use**: After creating new migrations or when setting up a fresh environment

### `setup_unclassified_system.py`
**Purpose**: Set up the unclassified product type system  
**Usage**: `python scripts/setup_unclassified_system.py`  
**When to use**: 
- Initial setup of the unclassified product type (ID 0)
- After database resets
- When setting up new development environments

## Running Scripts

From the `backend/` directory:

```bash
# Run all migrations
python scripts/run_migrations.py

# Set up unclassified product type system
python scripts/setup_unclassified_system.py
```

## What the Unclassified System Does

The unclassified system creates a special product type with ID 0 that:
- Acts as a wildcard for products not yet classified
- Prevents NULL foreign keys in the database
- Improves performance by eliminating NULL checks
- Provides consistent data structure

## Notes

- Scripts automatically handle Python path configuration
- All scripts run within Flask application context
- Error handling includes detailed tracebacks for debugging
- Scripts are safe to run multiple times (idempotent) 