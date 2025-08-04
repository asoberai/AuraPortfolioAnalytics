"""
AuraQuant Credential Setup Script
Demonstrates all credential configuration methods with your actual LimeTrader credentials
"""

import os
import json
from typing import Dict

# Your LimeTrader credentials
CREDENTIALS = {
    "username": "armaan0oberai@gmail.com",
    "password": "<your_password>",  # You need to fill this in
    "client_id": "trading-app-dmo-c383", 
    "client_secret": "4aa00156c97b4ba3952e81fa3e3d7159",
    "grant_type": "password",
    "base_url": "https://api.lime.co",
    "auth_url": "https://auth.lime.co"
}


def setup_env_file():
    """Create .env file with your credentials"""
    env_content = f"""# LimeTrader SDK Credentials
LIME_SDK_USERNAME={CREDENTIALS['username']}
LIME_SDK_PASSWORD={CREDENTIALS['password']}
LIME_SDK_CLIENT_ID={CREDENTIALS['client_id']}
LIME_SDK_CLIENT_SECRET={CREDENTIALS['client_secret']}
LIME_SDK_GRANT_TYPE={CREDENTIALS['grant_type']}
LIME_SDK_BASE_URL={CREDENTIALS['base_url']}
LIME_SDK_AUTH_URL={CREDENTIALS['auth_url']}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with your credentials")
    print("⚠️  Remember to update LIME_SDK_PASSWORD with your actual password!")


def setup_credentials_json():
    """Update credentials.json with your credentials"""
    with open('credentials.json', 'w') as f:
        json.dump(CREDENTIALS, f, indent=4)
    
    print("✅ Updated credentials.json with your credentials")
    print("⚠️  Remember to update password with your actual password!")


def test_all_credential_methods():
    """Test all credential loading methods"""
    print("🧪 Testing all credential configuration methods...")
    
    try:
        from lime_trader import LimeClient
        sdk_available = True
    except ImportError:
        print("⚠️  Official LimeTrader SDK not available - showing configuration only")
        sdk_available = False
        return
    
    # Method 1: from_file
    try:
        print("\n1️⃣ Testing credentials.json file method...")
        client = LimeClient.from_file("credentials.json")
        print("✅ credentials.json method works!")
    except Exception as e:
        print(f"❌ credentials.json method failed: {e}")
    
    # Method 2: from_env
    try:
        print("\n2️⃣ Testing environment variables method...")
        client = LimeClient.from_env()
        print("✅ Environment variables method works!")
    except Exception as e:
        print(f"❌ Environment variables method failed: {e}")
    
    # Method 3: from_env_file
    try:
        print("\n3️⃣ Testing .env file method...")
        client = LimeClient.from_env_file(".env")
        print("✅ .env file method works!")
    except Exception as e:
        print(f"❌ .env file method failed: {e}")
    
    # Method 4: from_json
    try:
        print("\n4️⃣ Testing JSON string method...")
        json_str = json.dumps(CREDENTIALS)
        client = LimeClient.from_json(json_str)
        print("✅ JSON string method works!")
    except Exception as e:
        print(f"❌ JSON string method failed: {e}")
    
    # Method 5: from_dict
    try:
        print("\n5️⃣ Testing dictionary method...")
        client = LimeClient.from_dict(CREDENTIALS)
        print("✅ Dictionary method works!")
    except Exception as e:
        print(f"❌ Dictionary method failed: {e}")


def get_password_securely():
    """Helper to get password securely"""
    import getpass
    
    print("\n🔐 Enter your LimeTrader password securely:")
    password = getpass.getpass("Password: ")
    return password


def setup_with_real_password():
    """Set up credentials with real password input"""
    password = get_password_securely()
    
    # Update credentials with real password
    real_credentials = CREDENTIALS.copy()
    real_credentials['password'] = password
    
    # Update .env file
    env_content = f"""# LimeTrader SDK Credentials
LIME_SDK_USERNAME={real_credentials['username']}
LIME_SDK_PASSWORD={real_credentials['password']}
LIME_SDK_CLIENT_ID={real_credentials['client_id']}
LIME_SDK_CLIENT_SECRET={real_credentials['client_secret']}
LIME_SDK_GRANT_TYPE={real_credentials['grant_type']}
LIME_SDK_BASE_URL={real_credentials['base_url']}
LIME_SDK_AUTH_URL={real_credentials['auth_url']}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # Update credentials.json
    with open('credentials.json', 'w') as f:
        json.dump(real_credentials, f, indent=4)
    
    print("✅ Updated both .env and credentials.json with your actual password!")
    print("🔒 Your password is now securely stored in the configuration files")


def test_connection():
    """Test connection with configured credentials"""
    try:
        from lime_trader import LimeClient
        
        print("\n🔌 Testing connection to LimeTrader API...")
        
        # Try different methods until one works
        methods = [
            ("Environment variables", lambda: LimeClient.from_env()),
            ("credentials.json file", lambda: LimeClient.from_file("credentials.json")),
            (".env file", lambda: LimeClient.from_env_file(".env"))
        ]
        
        for method_name, method_func in methods:
            try:
                print(f"Trying {method_name}...")
                client = method_func()
                
                # Test the connection
                account_info = client.account.get()
                print(f"✅ Connection successful using {method_name}!")
                print(f"Account Info: {account_info}")
                return client
                
            except Exception as e:
                print(f"❌ {method_name} failed: {e}")
                continue
        
        print("❌ All connection methods failed")
        return None
        
    except ImportError:
        print("❌ LimeTrader SDK not available")
        return None


def main():
    """Main setup function"""
    print("🚀 AuraQuant - LimeTrader Credential Setup")
    print("=" * 50)
    
    print("\nYour LimeTrader credentials:")
    print(f"Username: {CREDENTIALS['username']}")
    print(f"Client ID: {CREDENTIALS['client_id']}")
    print(f"Client Secret: {CREDENTIALS['client_secret'][:8]}...")
    print(f"Base URL: {CREDENTIALS['base_url']}")
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Set up .env file (template)")
        print("2. Set up credentials.json")
        print("3. Set up with real password (secure input)")
        print("4. Test all credential methods")
        print("5. Test connection")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            setup_env_file()
        elif choice == '2':
            setup_credentials_json()
        elif choice == '3':
            setup_with_real_password()
        elif choice == '4':
            test_all_credential_methods()
        elif choice == '5':
            test_connection()
        elif choice == '6':
            print("👋 Setup complete!")
            break
        else:
            print("❌ Invalid choice, please try again")


if __name__ == "__main__":
    main() 