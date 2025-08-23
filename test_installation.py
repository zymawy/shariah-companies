#!/usr/bin/env python3
"""
Test script to verify installation
"""
import sys
import importlib

def test_import(module_name, package_name=None):
    """Test if a module can be imported"""
    try:
        if package_name:
            importlib.import_module(module_name, package_name)
        else:
            importlib.import_module(module_name)
        return True, "OK"
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    print("=" * 50)
    print("Testing Argaam Scraper Installation")
    print("=" * 50)
    
    # Test core packages
    print("\n1. Testing Core Packages:")
    core_packages = [
        ("selenium", "Selenium WebDriver"),
        ("bs4", "BeautifulSoup4"),
        ("requests", "Requests"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy")
    ]
    
    all_ok = True
    for package, name in core_packages:
        success, msg = test_import(package)
        status = "✓" if success else "✗"
        print(f"   {status} {name}: {msg}")
        if not success:
            all_ok = False
    
    # Test optional packages
    print("\n2. Testing Optional Packages:")
    optional_packages = [
        ("arabic_reshaper", "Arabic Reshaper"),
        ("bidi", "Python Bidi"),
        ("sqlalchemy", "SQLAlchemy"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("loguru", "Loguru"),
        ("dotenv", "Python Dotenv"),
        ("schedule", "Schedule")
    ]
    
    for package, name in optional_packages:
        success, msg = test_import(package)
        status = "✓" if success else "✗"
        print(f"   {status} {name}: {msg if success else 'Not installed (optional)'}")
    
    # Test project modules
    print("\n3. Testing Project Modules:")
    sys.path.insert(0, '.')
    
    project_modules = [
        ("config", "Configuration"),
        ("src.utils.logger", "Logger"),
        ("src.utils.arabic_utils", "Arabic Utils"),
        ("src.scraper.enhanced_scraper", "Enhanced Scraper"),
        ("src.processors.classifier", "Classifier"),
        ("src.exporters.json_exporter", "JSON Exporter"),
        ("src.exporters.csv_exporter", "CSV Exporter"),
        ("src.exporters.excel_exporter", "Excel Exporter")
    ]
    
    project_ok = True
    for module, name in project_modules:
        success, msg = test_import(module)
        status = "✓" if success else "✗"
        print(f"   {status} {name}: {msg}")
        if not success:
            project_ok = False
    
    # Test Chrome/ChromeDriver
    print("\n4. Testing Chrome/ChromeDriver:")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("   ✓ Selenium imports OK")
        print("   ✓ WebDriver Manager OK")
        
        # Don't actually start Chrome in test
        print("   ℹ Chrome browser test skipped (run main.py to test)")
        
    except Exception as e:
        print(f"   ✗ Chrome setup issue: {str(e)}")
        all_ok = False
    
    # Check directories
    print("\n5. Checking Directories:")
    import os
    
    directories = [
        "data/raw",
        "data/processed",
        "data/exports",
        "logs"
    ]
    
    for directory in directories:
        exists = os.path.exists(directory)
        status = "✓" if exists else "✗"
        print(f"   {status} {directory}/")
        if not exists:
            print(f"      Creating {directory}/...")
            os.makedirs(directory, exist_ok=True)
    
    # Check .env file
    print("\n6. Checking Configuration:")
    env_exists = os.path.exists(".env")
    status = "✓" if env_exists else "✗"
    print(f"   {status} .env file")
    if not env_exists:
        print("      Creating .env from .env.example...")
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("      ✓ .env file created")
    
    # Summary
    print("\n" + "=" * 50)
    if all_ok and project_ok:
        print("✓ Installation looks good!")
        print("\nYou can now run:")
        print("  python main.py")
    else:
        print("⚠ Some issues detected")
        print("\nTry running:")
        print("  python setup.py")
        print("\nOr install missing packages:")
        print("  pip install -r requirements-minimal.txt")
    print("=" * 50)

if __name__ == "__main__":
    main()