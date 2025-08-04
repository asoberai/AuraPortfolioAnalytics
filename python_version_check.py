"""
Python Version Compatibility Checker for AuraQuant
LimeTrader SDK requires Python 3.10+
"""

import sys
import platform


def check_python_version():
    """Check if current Python version is compatible with LimeTrader SDK"""
    
    current_version = sys.version_info
    required_version = (3, 10)
    
    print("🐍 Python Version Compatibility Check")
    print("=" * 40)
    print(f"Current Python: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Required: Python {required_version[0]}.{required_version[1]}+")
    
    if current_version >= required_version:
        print("✅ Python version is compatible with LimeTrader SDK!")
        return True
    else:
        print("❌ Python version is too old for LimeTrader SDK")
        print(f"\nYour version: {current_version.major}.{current_version.minor}.{current_version.micro}")
        print(f"Required: {required_version[0]}.{required_version[1]}+")
        print("\n🔧 Solutions:")
        print("1. Upgrade to Python 3.10+ using pyenv:")
        print("   pyenv install 3.13.0")
        print("   pyenv local 3.13.0")
        print("\n2. Or use conda:")
        print("   conda create -n lime_env python=3.13")
        print("   conda activate lime_env")
        print("\n3. Or upgrade system Python (if using brew):")
        print("   brew install python@3.13")
        
        return False


def check_sdk_availability():
    """Check if LimeTrader SDK can be imported"""
    try:
        import lime_trader
        print("✅ LimeTrader SDK is available!")
        return True
    except ImportError:
        print("⚠️  LimeTrader SDK not installed")
        print("💡 Install when available: pip install lime-trader-sdk")
        return False


def main():
    """Main compatibility check"""
    python_ok = check_python_version()
    
    if python_ok:
        print("\n" + "=" * 40)
        sdk_ok = check_sdk_availability()
        
        if sdk_ok:
            print("\n🚀 Ready for LimeTrader connection!")
        else:
            print("\n⏳ Ready for SDK installation when available")
    else:
        print("\n⚠️  Please upgrade Python before using LimeTrader SDK")


if __name__ == "__main__":
    main() 