#!/usr/bin/env python3
"""
Test script for email service implementations.
This script tests both MailerSend and SMTP providers.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.thirdparty.mailersend import MailerSendAdapter
from server.thirdparty.smtp import SMTPAdapter
from server.services.email_service import EmailService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mailersend():
    """Test MailerSend implementation."""
    print("\n=== Testing MailerSend ===")
    
    client = MailerSendAdapter()
    
    if not client.is_configured:
        print("❌ MailerSend not configured (MAILERSEND_API_KEY not set)")
        return False
    
    print(f"✅ MailerSend configured")
    print(f"   From: {client.get_from_name()} <{client.get_from_email()}>")
    
    # Test email (uncomment to actually send)
    # result = client.send_email(
    #     to_email="test@example.com",
    #     subject="Test Email",
    #     text_content="This is a test email from MailerSend",
    #     html_content="<h1>Test Email</h1><p>This is a test email from MailerSend</p>"
    # )
    # print(f"   Send result: {result}")
    
    return True

def test_smtp():
    """Test SMTP implementation."""
    print("\n=== Testing SMTP ===")
    
    client = SMTPAdapter()
    
    if not client.is_configured:
        print("❌ SMTP not configured (SMTP_USERNAME/SMTP_PASSWORD not set)")
        return False
    
    print(f"✅ SMTP configured")
    print(f"   Server: {client.smtp_server}:{client.smtp_port}")
    print(f"   TLS: {client.use_tls}")
    print(f"   From: {client.get_from_name()} <{client.get_from_email()}>")
    
    # Test email (uncomment to actually send)
    # result = client.send_email(
    #     to_email="test@example.com",
    #     subject="Test Email",
    #     text_content="This is a test email from SMTP",
    #     html_content="<h1>Test Email</h1><p>This is a test email from SMTP</p>"
    # )
    # print(f"   Send result: {result}")
    
    return True

def test_email_service():
    """Test EmailService with auto-detection."""
    print("\n=== Testing EmailService ===")
    
    service = EmailService()
    
    # Test auto-detection
    service.init_app(None)  # Pass None for app since we're just testing
    
    if not service.is_configured:
        print("❌ EmailService not configured")
        return False
    
    info = service.get_provider_info()
    print(f"✅ EmailService configured with {info['provider']} provider")
    print(f"   From: {info['from_name']} <{info['from_email']}>")
    
    if info['provider'] == 'smtp':
        print(f"   SMTP Server: {info['server']}:{info['port']}")
    
    return True

def main():
    """Run all tests."""
    print("Email Service Test Suite")
    print("=" * 50)
    
    # Check environment variables
    print("\nEnvironment Variables:")
    mailersend_key = os.getenv('MAILERSEND_API_KEY')
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    
    print(f"   MAILERSEND_API_KEY: {'✅ Set' if mailersend_key else '❌ Not set'}")
    print(f"   SMTP_USERNAME: {'✅ Set' if smtp_user else '❌ Not set'}")
    print(f"   SMTP_PASSWORD: {'✅ Set' if smtp_pass else '❌ Not set'}")
    
    # Run tests
    mailersend_ok = test_mailersend()
    smtp_ok = test_smtp()
    service_ok = test_email_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"   MailerSend: {'✅ Pass' if mailersend_ok else '❌ Fail'}")
    print(f"   SMTP: {'✅ Pass' if smtp_ok else '❌ Fail'}")
    print(f"   EmailService: {'✅ Pass' if service_ok else '❌ Fail'}")
    
    if not any([mailersend_ok, smtp_ok]):
        print("\n⚠️  No email providers configured!")
        print("   Set MAILERSEND_API_KEY or SMTP_USERNAME/SMTP_PASSWORD")
        print("   See EMAIL_CONFIGURATION.md for details")

if __name__ == "__main__":
    main()
