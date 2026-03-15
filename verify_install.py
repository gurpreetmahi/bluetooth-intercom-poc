"""
Quick verification script - checks if all dependencies are available
"""

import sys

def check_package(package_name, import_name=None):
    """Check if a package can be imported"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name:20s} - OK")
        return True
    except ImportError as e:
        print(f"❌ {package_name:20s} - MISSING: {e}")
        return False


def main():
    """Main verification"""
    print("\n" + "="*60)
    print("DEPENDENCY VERIFICATION")
    print("="*60)
    print(f"\nPython Version: {sys.version}")
    print(f"Python Path: {sys.executable}\n")
    
    print("Checking required packages:\n")
    
    packages = [
        ("PyAudio", "pyaudio"),
        ("NumPy", "numpy"),
        ("pywin32", "win32com.client"),
        ("comtypes", "comtypes"),
        ("PyYAML", "yaml"),
        ("colorama", "colorama"),
        ("pytest", "pytest"),
    ]
    
    results = []
    for package_name, import_name in packages:
        results.append(check_package(package_name, import_name))
    
    print("\n" + "="*60)
    if all(results):
        print("✅ ALL DEPENDENCIES INSTALLED!")
        print("="*60)
        print("\nYou're ready to run the Bluetooth Intercom!")
        print("\nQuick tests:")
        print("  python src\\test_loopback.py")
        print("  python src\\bluetooth_intercom_test.py")
        print()
        return 0
    else:
        print("❌ MISSING DEPENDENCIES")
        print("="*60)
        print("\nInstall missing packages:")
        print("  pip install pyaudio numpy pywin32 comtypes PyYAML colorama pytest")
        print("\nOr see INSTALL_PYTHON313.md for Python 3.13 specific instructions")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
