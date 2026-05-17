#!/usr/bin/env python3
"""
Email Configuration Test Script

This script tests the email configuration and sends a test email.
Run this after setting up your MAILERSEND_API_KEY.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from server import create_server
from server.services.email_service import EmailService

def test_email_configuration():
    """Test email configuration and send a test email."""
    
    print("🔧 Testing Email Configuration...")
    print("=" * 50)
    
    # Create server instance
    app = create_server()
    
    with app.app_context():
        try:
            # Initialize email service
            email_service = EmailService()
            email_service.init_app(app)
            
            # Check configuration
            print(f"📨 From Email: {email_service.from_email}")
            print(f"🏷️  From Name: {email_service.from_name}")
            print(f"🌐 Frontend URL: {email_service.base_url}")
            print(f"✅ Configured: {email_service.is_configured}")
            print()
            
            if not email_service.is_configured:
                print("❌ Email service is not configured!")
                print("📋 Please set the following environment variable:")
                print("   - MAILERSEND_API_KEY")
                print()
                print("📖 Get your API key from: https://www.mailersend.com/")
                return False
            
            # Test sending a verification email
            print("📤 Testing email sending...")
            test_email = input("Enter test email address (or press Enter to skip): ").strip()
            
            if test_email:
                result = email_service.send_verification_email(
                    email=test_email,
                    first_name="Test User",
                    token="test-token-12345"
                )
                
                if result.get('success'):
                    print("✅ Test email sent successfully!")
                    print(f"📧 Check {test_email} for the verification email.")
                else:
                    print("❌ Failed to send test email:")
                    print(f"   Error: {result.get('error', 'Unknown error')}")
                    return False
            else:
                print("⏭️  Skipping email send test.")
            
            print()
            print("✅ Email configuration test completed successfully!")
            print("🚀 Your email service is ready to use.")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during email configuration test: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_email_configuration()
    sys.exit(0 if success else 1)

