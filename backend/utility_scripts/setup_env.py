#!/usr/bin/env python3
"""
Environment Setup Script for Go Postal SD

This script helps configure the environment variables for different deployment scenarios.
"""

import os
import sys
import secrets
from datetime import datetime
from pathlib import Path


def generate_secret_key():
    """Generate a secure secret key."""
    return secrets.token_urlsafe(32)


def create_env_file(environment='development'):
    """Create .env file based on environment."""
    env_file = Path('.env')
    
    if env_file.exists():
        print(f"⚠️  .env file already exists. Backing up to .env.backup")
        env_file.rename('.env.backup')
    
    # Base configuration
    config = {
        'development': {
            'ENVIRONMENT': 'development',
            'FRONTEND_URL': 'http://localhost:3000',
            'DATABASE_URL': 'sqlite:///instance/gopostalsd.db',
            'DEBUG': 'true',
            'LOG_LEVEL': 'DEBUG',
            'SESSION_COOKIE_SECURE': 'false',
        },
        'staging': {
            'ENVIRONMENT': 'staging',
            'FRONTEND_URL': 'https://staging.gopostalsd.com',
            'DATABASE_URL': 'postgresql://username:password@localhost:5432/gopostalsd_staging',
            'DEBUG': 'false',
            'LOG_LEVEL': 'INFO',
            'SESSION_COOKIE_SECURE': 'true',
        },
        'production': {
            'ENVIRONMENT': 'production',
            'FRONTEND_URL': 'https://gopostalsd.com',
            'DATABASE_URL': 'postgresql://username:password@localhost:5432/gopostalsd',
            'DEBUG': 'false',
            'LOG_LEVEL': 'WARNING',
            'SESSION_COOKIE_SECURE': 'true',
        }
    }
    
    # Common configuration
    common_config = {
        'SECRET_KEY': generate_secret_key(),
        'JWT_SECRET_KEY': generate_secret_key(),
        'SESSION_COOKIE_HTTPONLY': 'true',
        'SESSION_COOKIE_SAMESITE': 'Lax',
        
        # Email configuration (SMTP)
        'SMTP_HOST': 'smtp.gmail.com',
        'SMTP_PORT': '587',
        'SMTP_USERNAME': 'your_email@gmail.com',
        'SMTP_PASSWORD': 'your_app_password_here',
        'SMTP_FROM_EMAIL': 'noreply@gopostalsd.com',
        'SMTP_FROM_NAME': 'Go Postal SD',
        'SMTP_USE_TLS': 'true',
        
        # Third-party services
        'SINALITE_CLIENT_ID': 'your_sinalite_client_id_here',
        'SINALITE_CLIENT_SECRET': 'your_sinalite_client_secret_here',
        'SINALITE_BASE_URL_DEV': 'https://apiconnect.sinalite.com',
        'SINALITE_BASE_URL': 'https://apiconnect.sinalite.com',
        
        'SUPABASE_URL': 'your_supabase_url_here',
        'SUPABASE_KEY': 'your_supabase_anon_key_here',
        'SUPABASE_BUCKET': 'gopostalsd-uploads',
        
        'SQUARE_ACCESS_TOKEN': 'your_square_access_token_here',
        'SQUARE_APPLICATION_ID': 'your_square_application_id_here',
        'SQUARE_LOCATION_ID': 'your_square_location_id_here',
        'SQUARE_ENVIRONMENT': 'sandbox',
    }
    
    # Merge configurations
    final_config = {**common_config, **config[environment]}
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(f"# Go Postal SD Environment Configuration\n")
        f.write(f"# Generated for {environment} environment\n")
        f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("# =============================================================================\n")
        f.write("# APPLICATION CONFIGURATION\n")
        f.write("# =============================================================================\n")
        f.write(f"ENVIRONMENT={final_config['ENVIRONMENT']}\n")
        f.write(f"FRONTEND_URL={final_config['FRONTEND_URL']}\n")
        f.write(f"DEBUG={final_config['DEBUG']}\n")
        f.write(f"LOG_LEVEL={final_config['LOG_LEVEL']}\n\n")
        
        f.write("# =============================================================================\n")
        f.write("# DATABASE CONFIGURATION\n")
        f.write("# =============================================================================\n")
        f.write(f"DATABASE_URL={final_config['DATABASE_URL']}\n\n")
        
        f.write("# =============================================================================\n")
        f.write("# SECURITY CONFIGURATION\n")
        f.write("# =============================================================================\n")
        f.write(f"SECRET_KEY={final_config['SECRET_KEY']}\n")
        f.write(f"JWT_SECRET_KEY={final_config['JWT_SECRET_KEY']}\n")
        f.write(f"SESSION_COOKIE_SECURE={final_config['SESSION_COOKIE_SECURE']}\n")
        f.write(f"SESSION_COOKIE_HTTPONLY={final_config['SESSION_COOKIE_HTTPONLY']}\n")
        f.write(f"SESSION_COOKIE_SAMESITE={final_config['SESSION_COOKIE_SAMESITE']}\n\n")
        
        f.write("# =============================================================================\n")
        f.write("# EMAIL CONFIGURATION\n")
        f.write("# =============================================================================\n")
        f.write(f"SMTP_HOST={final_config['SMTP_HOST']}\n")
        f.write(f"SMTP_PORT={final_config['SMTP_PORT']}\n")
        f.write(f"SMTP_USERNAME={final_config['SMTP_USERNAME']}\n")
        f.write(f"SMTP_PASSWORD={final_config['SMTP_PASSWORD']}\n")
        f.write(f"SMTP_FROM_EMAIL={final_config['SMTP_FROM_EMAIL']}\n")
        f.write(f"SMTP_FROM_NAME={final_config['SMTP_FROM_NAME']}\n")
        f.write(f"SMTP_USE_TLS={final_config['SMTP_USE_TLS']}\n\n")
        
        f.write("# =============================================================================\n")
        f.write("# THIRD-PARTY SERVICES\n")
        f.write("# =============================================================================\n")
        f.write(f"SINALITE_CLIENT_ID={final_config['SINALITE_CLIENT_ID']}\n")
        f.write(f"SINALITE_CLIENT_SECRET={final_config['SINALITE_CLIENT_SECRET']}\n")
        f.write(f"SINALITE_BASE_URL_DEV={final_config['SINALITE_BASE_URL_DEV']}\n")
        f.write(f"SINALITE_BASE_URL={final_config['SINALITE_BASE_URL']}\n")
        f.write(f"SUPABASE_URL={final_config['SUPABASE_URL']}\n")
        f.write(f"SUPABASE_KEY={final_config['SUPABASE_KEY']}\n")
        f.write(f"SUPABASE_BUCKET={final_config['SUPABASE_BUCKET']}\n")
        f.write(f"SQUARE_ACCESS_TOKEN={final_config['SQUARE_ACCESS_TOKEN']}\n")
        f.write(f"SQUARE_APPLICATION_ID={final_config['SQUARE_APPLICATION_ID']}\n")
        f.write(f"SQUARE_LOCATION_ID={final_config['SQUARE_LOCATION_ID']}\n")
        f.write(f"SQUARE_ENVIRONMENT={final_config['SQUARE_ENVIRONMENT']}\n\n")
        
        f.write("# =============================================================================\n")
        f.write("# NEXT STEPS\n")
        f.write("# =============================================================================\n")
        f.write("# 1. Update the placeholder values above with your actual credentials\n")
        f.write("# 2. For production, ensure FRONTEND_URL points to your domain\n")
        f.write("# 3. Configure your email provider (SMTP or MailerSend)\n")
        f.write("# 4. Set up your third-party service credentials\n")
        f.write("# 5. Run: python app.py\n")
    
    print(f"✅ Created .env file for {environment} environment")
    print(f"📧 Frontend URL set to: {final_config['FRONTEND_URL']}")
    print(f"🔑 Generated secure secret keys")
    print(f"\n📝 Next steps:")
    print(f"   1. Update placeholder values in .env file")
    print(f"   2. Configure your email provider credentials")
    print(f"   3. Set up third-party service credentials")
    print(f"   4. Run: python app.py")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        environment = sys.argv[1].lower()
        if environment not in ['development', 'staging', 'production']:
            print("❌ Invalid environment. Use: development, staging, or production")
            sys.exit(1)
    else:
        environment = 'development'
    
    print(f"🚀 Setting up Go Postal SD environment: {environment}")
    create_env_file(environment)


if __name__ == "__main__":
    main()
