#!/usr/bin/env python3
"""
Setup script for Argaam Shariah Companies Scraper
"""
import subprocess
import sys
import os

def install_package(package):
    """Install a single package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("=" * 50)
    print("Setting up Argaam Shariah Companies Scraper")
    print("=" * 50)
    
    # Upgrade pip first
    print("\n1. Upgrading pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Core dependencies (install these first)
    core_packages = [
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "lxml==4.9.3",
        "pandas==2.1.4",
        "numpy==1.24.3"
    ]
    
    print("\n2. Installing core packages...")
    for package in core_packages:
        print(f"   Installing {package}...")
        if not install_package(package):
            print(f"   Warning: Failed to install {package}")
    
    # Selenium and web driver
    print("\n3. Installing web scraping tools...")
    web_packages = [
        "selenium==4.15.2",
        "webdriver-manager==4.0.1"
    ]
    
    for package in web_packages:
        print(f"   Installing {package}...")
        if not install_package(package):
            print(f"   Warning: Failed to install {package}")
    
    # Arabic text processing
    print("\n4. Installing Arabic text processing...")
    arabic_packages = [
        "arabic-reshaper==3.0.0",
        "python-bidi==0.4.2"
    ]
    
    for package in arabic_packages:
        print(f"   Installing {package}...")
        if not install_package(package):
            print(f"   Warning: Failed to install {package}")
            print("   Note: Arabic text processing may not work properly")
    
    # Database and export
    print("\n5. Installing database and export tools...")
    db_packages = [
        "sqlalchemy==2.0.23",
        "openpyxl==3.1.2",
        "xlsxwriter==3.1.9"
    ]
    
    for package in db_packages:
        print(f"   Installing {package}...")
        if not install_package(package):
            print(f"   Warning: Failed to install {package}")
    
    # Utilities
    print("\n6. Installing utilities...")
    util_packages = [
        "python-dotenv==1.0.0",
        "schedule==1.2.0",
        "loguru==0.7.2"
    ]
    
    for package in util_packages:
        print(f"   Installing {package}...")
        if not install_package(package):
            print(f"   Warning: Failed to install {package}")
    
    # API (optional)
    print("\n7. Installing API dependencies (optional)...")
    api_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0"
    ]
    
    for package in api_packages:
        print(f"   Installing {package}...")
        if not install_package(package):
            print(f"   Note: API features will not be available")
    
    # Create necessary directories
    print("\n8. Creating directories...")
    directories = [
        "data/raw",
        "data/processed", 
        "data/exports",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   Created {directory}/")
    
    # Create .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("\n9. Creating .env file...")
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("   .env file created from .env.example")
        else:
            with open(".env", "w") as f:
                f.write("HEADLESS_MODE=True\n")
                f.write("LOG_LEVEL=INFO\n")
            print("   Basic .env file created")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)
    print("\nTo run the scraper:")
    print("  python main.py")
    print("\nTo start the API:")
    print("  python -m uvicorn src.api.main:app --reload")
    print("\nFor more options, see README.md")

if __name__ == "__main__":
    main()