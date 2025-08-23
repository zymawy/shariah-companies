# Installation Guide

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
python setup.py
```

This will:
- Upgrade pip
- Install all dependencies
- Create necessary directories
- Create .env file

### Option 2: Manual Installation

#### Step 1: Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Step 2: Upgrade pip
```bash
python -m pip install --upgrade pip
```

#### Step 3: Install Requirements
```bash
# Try full installation
pip install -r requirements.txt

# If you get errors, try minimal installation
pip install -r requirements-minimal.txt
```

#### Step 4: Create Directories
```bash
mkdir -p data/raw data/processed data/exports logs
```

#### Step 5: Create .env file
```bash
cp .env.example .env
```

## Troubleshooting

### Common Issues and Solutions

#### 1. numpy/pandas Installation Error
```bash
# Install specific versions
pip install numpy==1.24.3
pip install pandas==2.1.4
```

#### 2. lxml Installation Error (macOS)
```bash
# Install Xcode command line tools
xcode-select --install

# Then install lxml
pip install lxml
```

#### 3. lxml Installation Error (Linux)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install libxml2-dev libxslt-dev python3-dev

# Then install lxml
pip install lxml
```

#### 4. Arabic Libraries Error
```bash
# These are optional, skip if causing issues
pip install --no-deps arabic-reshaper
pip install --no-deps python-bidi
```

#### 5. Chrome/ChromeDriver Issues
The scraper uses `webdriver-manager` which automatically downloads ChromeDriver.
Make sure you have Google Chrome installed on your system.

**macOS:**
```bash
# Install Chrome via Homebrew
brew install --cask google-chrome
```

**Linux:**
```bash
# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
sudo apt-get update
sudo apt-get install google-chrome-stable
```

**Windows:**
Download and install Chrome from: https://www.google.com/chrome/

#### 6. Permission Errors
```bash
# Use user installation
pip install --user -r requirements.txt
```

#### 7. SSL Certificate Error
```bash
# Upgrade certificates
pip install --upgrade certifi

# Or use trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

## Minimal Installation

If you're still having issues, install only the core packages:

```bash
# Core packages only
pip install selenium beautifulsoup4 requests pandas

# Then install one by one
pip install webdriver-manager
pip install python-dotenv
pip install loguru
```

## Docker Installation (Alternative)

If you're having persistent issues, use Docker:

```bash
# Build and run with Docker
docker-compose up -d
```

## Verify Installation

Test your installation:

```bash
# Test imports
python -c "import selenium; import pandas; import bs4; print('Core packages OK')"

# Test scraper
python -c "from src.scraper.enhanced_scraper import EnhancedArgaamScraper; print('Scraper OK')"
```

## Platform-Specific Notes

### macOS (Apple Silicon M1/M2/M3)

**IMPORTANT: ChromeDriver Setup for Apple Silicon**

```bash
# Option 1: Run our installation script
chmod +x install_chromedriver.sh
./install_chromedriver.sh

# Option 2: Manual installation via Homebrew
brew install --cask chromedriver

# Allow ChromeDriver in macOS security settings
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver

# If you get "developer cannot be verified" error:
# Go to System Settings > Privacy & Security > Allow Anyway
```

**Python Setup:**
```bash
# Some packages might need Rosetta
softwareupdate --install-rosetta

# Use conda for better compatibility (optional)
conda create -n argaam python=3.10
conda activate argaam
pip install -r requirements.txt
```

**Troubleshooting Apple Silicon Issues:**
1. If ChromeDriver doesn't work, ensure you have the ARM64 version:
   ```bash
   file /opt/homebrew/bin/chromedriver
   # Should show "arm64" in output
   ```

2. If you get permission errors:
   ```bash
   sudo spctl --master-disable  # Temporarily disable Gatekeeper
   # Run your script
   sudo spctl --master-enable   # Re-enable Gatekeeper
   ```

3. Alternative: Use Docker (no ChromeDriver needed):
   ```bash
   docker-compose up -d
   ```

### Windows
- Use Python 3.10 or 3.11 (not 3.12 yet)
- Run Command Prompt as Administrator
- Install Visual C++ Build Tools if needed

### Linux (Ubuntu/Debian)
```bash
# Install Python development packages
sudo apt-get install python3-dev python3-pip python3-venv

# Install build essentials
sudo apt-get install build-essential
```

## Still Having Issues?

1. **Use minimal requirements:**
   ```bash
   pip install -r requirements-minimal.txt
   ```

2. **Install packages one by one:**
   ```bash
   pip install selenium
   pip install beautifulsoup4
   pip install pandas
   # etc...
   ```

3. **Use Docker:** See Docker section in README.md

4. **Check Python version:**
   ```bash
   python --version  # Should be 3.8 or higher
   ```

5. **Clear pip cache:**
   ```bash
   pip cache purge
   ```

## Contact

If you continue to have issues, please open an issue on GitHub with:
- Your operating system
- Python version
- The exact error message
- Steps you've tried