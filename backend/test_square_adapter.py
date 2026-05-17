#!/usr/bin/env python3
"""
Test script for Square Payment adapter.
This script tests the SquareAdapter functionality.
"""

import os
import sys
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

from server.thirdparty.square import SquareAdapter
from server.services.payment_service import PaymentService

def test_square_adapter():
    """Test Square adapter functionality."""
    print("🔧 Testing Square Payment Adapter...")
    print("=" * 60)
    
    try:
        # Test adapter initialization
        print("📱 Initializing Square adapter...")
        square_adapter = SquareAdapter()
        
        if not square_adapter.is_configured:
            print("⚠️ Square adapter not configured")
            print("   Set the following environment variables:")
            print("   - SQUARE_ACCESS_TOKEN")
            print("   - SQUARE_APPLICATION_ID") 
            print("   - SQUARE_LOCATION_ID")
            print("   - SQUARE_ENVIRONMENT (optional, defaults to 'sandbox')")
            return False
        
        print("✅ Square adapter initialized successfully")
        
        # Test configuration info
        print("\n📋 Configuration Info:")
        info = square_adapter.get_square_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Test payment service
        print("\n💳 Testing Payment Service...")
        payment_service = PaymentService(provider='square')
        
        if payment_service.is_configured:
            print("✅ Payment service configured successfully")
        else:
            print("❌ Payment service not configured")
            return False
        
        # Test service info
        print("\n📊 Payment Service Info:")
        service_info = payment_service.get_provider_info()
        for key, value in service_info.items():
            print(f"   {key}: {value}")
        
        print("\n" + "=" * 60)
        print("🎉 Square Payment Adapter test completed successfully!")
        print("=" * 60)
        print("💡 Next Steps:")
        print("1. Set up Square Developer account")
        print("2. Configure environment variables")
        print("3. Test with Square Web Payments SDK")
        print("4. Implement frontend payment forms")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Square adapter: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_payment_service():
    """Test payment service functionality."""
    print("\n🔧 Testing Payment Service...")
    print("=" * 60)
    
    try:
        # Test different providers
        providers = ['square']
        
        for provider in providers:
            print(f"\n📱 Testing {provider} provider...")
            payment_service = PaymentService(provider=provider)
            
            if payment_service.is_configured:
                print(f"✅ {provider} payment service configured")
            else:
                print(f"⚠️ {provider} payment service not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing payment service: {str(e)}")
        return False

def main():
    """Main function."""
    print("🚀 Go Postal SD - Square Payment Adapter Test")
    print("=" * 60)
    
    # Test Square adapter
    square_success = test_square_adapter()
    
    # Test payment service
    service_success = test_payment_service()
    
    if square_success and service_success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
