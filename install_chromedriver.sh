#!/bin/bash

# ChromeDriver Installation Script for Apple Silicon Macs
echo "================================================"
echo "ChromeDriver Installation for Apple Silicon Mac"
echo "================================================"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "This script is for macOS only"
    exit 1
fi

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo ""
echo "Installing ChromeDriver via Homebrew..."
brew install --cask chromedriver

# For Apple Silicon, we might need to approve the driver
echo ""
echo "Attempting to approve ChromeDriver for macOS Gatekeeper..."
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver 2>/dev/null || true

# Test if ChromeDriver is accessible
if [ -f "/opt/homebrew/bin/chromedriver" ]; then
    echo ""
    echo "✓ ChromeDriver installed successfully at: /opt/homebrew/bin/chromedriver"
    
    # Get version
    /opt/homebrew/bin/chromedriver --version
    
    echo ""
    echo "Setup complete! The scraper should now work."
else
    echo ""
    echo "⚠ ChromeDriver installation may have failed."
    echo "Try running: brew reinstall chromedriver"
fi

echo ""
echo "If you still have issues, try:"
echo "1. Open System Preferences > Security & Privacy"
echo "2. Click 'Allow Anyway' for ChromeDriver if prompted"
echo "3. Run: sudo spctl --master-disable (to temporarily disable Gatekeeper)"
echo ""