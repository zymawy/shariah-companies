# Argaam Shariah Companies Scraper | أداة استخراج بيانات الشركات الشرعية من أرقام

A comprehensive Python scraper for extracting Shariah-compliant companies data from Argaam.com, organized by market (تاسي/نمو) and Shariah certification board.

## 🌟 Features

- **Institution-Based Scraping**: Directly accesses data for each Shariah institution:
  - الراجحي المالية (Al Rajhi Financial)
  - د.محمد بن سعود العصيمي (Dr. Muhammad bin Saud Al-Osaimi)
  - تنمية للاستثمار (Development for Investment)
  - البلاد المالية (Al-Bilad Financial)

- **Market Coverage**:
  - **TASI (تاسي)**: Main market companies
  - **NOMU (نمو)**: Parallel market companies
  - Automatic market detection and classification

- **Data Extraction**:
  - Company name and code
  - Market classification
  - Shariah board certification
  - Purification amounts (مبلغ التطهير) when available
  - Sector and subsector information

- **Export Formats**:
  - JSON (flat and hierarchical)
  - CSV (with market-specific files)
  - Excel (multi-sheet workbooks)
  - SQLite database

- **Additional Features**:
  - REST API with FastAPI
  - Scheduled automated scraping
  - Docker support
  - Apple Silicon (M1/M2/M3) compatibility

## 📋 Prerequisites

- Python 3.8+
- Google Chrome browser
- ChromeDriver (automatically installed)

## 🚀 Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/almaqased.git
cd almaqased

# Install dependencies
pip install -r requirements.txt

# For Apple Silicon Macs (M1/M2/M3)
brew install chromedriver
```

### Apple Silicon (M1/M2/M3) Setup

For Apple Silicon Macs, you need to install ChromeDriver via Homebrew:

```bash
# Install ChromeDriver
brew install chromedriver

# Remove quarantine flag (if needed)
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

### Alternative Installation

```bash
# Using setup.py
python setup.py install

# Minimal installation
pip install -r requirements-minimal.txt
```

## 🎯 Usage

### Basic Usage

```bash
# Run the scraper with default settings (scrapes all markets and institutions)
python main.py

# Scrape TASI market only
python main.py --market TASI

# Scrape NOMU market only
python main.py --market NOMU

# Export to specific format
python main.py --export-format json
python main.py --export-format csv
python main.py --export-format excel
```

### Test Scripts

```bash
# Test institution-based scraper
python test_institution_scraper.py

# Test NOMU market specifically
python test_nomu_scraper.py

# Test enhanced scraper
python test_scraper.py
```

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --export-format   Export format: json, csv, excel, or all (default: all)
  --market         Filter by market: TASI, NOMU, تاسي, or نمو
  --shariah-board  Filter by specific Shariah board name
  --headless       Run browser in headless mode (default: True)
  --scraper        Choose scraper: institution or enhanced (default: institution)
```

## 📊 Data Structure

### Company Data Format

```json
{
  "timestamp": "2025-08-23T10:00:00",
  "company_code": "1120",
  "company_name": "مصرف الراجحي",
  "ticker_symbol": "1120",
  "market": "تاسي",
  "shariah_board": "الراجحي المالية",
  "sector": "البنوك",
  "subsector": "",
  "classification": "شرعي",
  "purification_amount": 0.05  // When available (SAR per share)
}
```

### Export Files

All exported files are saved in the `data/exports/` directory:

- `companies_flat_[timestamp].json` - All companies in a flat array
- `companies_hierarchical_[timestamp].json` - Nested by market and board
- `companies_by_market_[timestamp].json` - Grouped by market
- `companies_by_board_[timestamp].json` - Grouped by Shariah board
- `companies_[timestamp].csv` - CSV format
- `companies_complete_[timestamp].xlsx` - Multi-sheet Excel

## 🔄 API Usage

### Starting the API Server

```bash
# Start the FastAPI server
python api.py

# Access API documentation
# http://localhost:8000/docs
```

### API Endpoints

```bash
# Get all companies
GET http://localhost:8000/api/companies

# Get companies by market
GET http://localhost:8000/api/companies?market=TASI
GET http://localhost:8000/api/companies?market=NOMU

# Get companies by Shariah board
GET http://localhost:8000/api/companies?shariah_board=الراجحي المالية

# Get statistics
GET http://localhost:8000/api/statistics

# Trigger manual scraping
POST http://localhost:8000/api/scrape
```

## 🐳 Docker Support

```bash
# Build Docker image
docker build -t argaam-scraper .

# Run container
docker run -d -p 8000:8000 argaam-scraper

# With volume for data persistence
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data argaam-scraper
```

## ⏰ Scheduled Scraping

The scraper includes a scheduler that automatically runs daily updates:

```bash
# Run the scheduler
python scheduler.py

# Configure update interval (in hours) via environment variable
export UPDATE_INTERVAL_HOURS=24
python scheduler.py
```

## 📁 Project Structure

```
almaqased/
├── config.py                 # Configuration settings
├── main.py                  # Main entry point
├── api.py                   # FastAPI REST API
├── scheduler.py             # Automated scheduling
├── src/
│   ├── scraper/
│   │   ├── argaam_institution_scraper.py  # Institution-based scraper
│   │   └── enhanced_scraper.py            # Enhanced scraper
│   ├── processors/
│   │   └── classifier.py    # Company classification
│   ├── exporters/
│   │   ├── json_exporter.py # JSON export
│   │   ├── csv_exporter.py  # CSV export
│   │   └── excel_exporter.py # Excel export
│   ├── models/
│   │   └── company.py       # SQLAlchemy models
│   └── utils/
│       ├── logger.py        # Logging utilities
│       └── arabic_utils.py  # Arabic text processing
├── data/
│   ├── exports/            # Exported files
│   ├── raw/               # Raw scraped data
│   └── processed/         # Processed data
└── logs/                  # Application logs
```

## 🔍 How It Works

The scraper uses Selenium WebDriver to navigate Argaam's Shariah companies pages:

1. **Institution-Based Approach**: Directly accesses each institution's page using the URL pattern:
   ```
   https://www.argaam.com/ar/company/shariahcompaniesbyinstitution/{institution_id}?marketid={market_id}
   ```
   - Institution IDs: 1 (Al Rajhi), 2 (Dr. Al-Osaimi), 3 (Development), 6 (Al-Bilad)
   - Market IDs: 3 (TASI), 14 (NOMU)

2. **Data Extraction**: Parses HTML tables to extract company information

3. **Classification**: Organizes companies by market and Shariah board

4. **Export**: Saves data in multiple formats for different use cases

## 📊 Statistics

Based on latest scraping (August 2025):

### TASI Market (السوق الرئيسية)
- الراجحي المالية: ~243 companies
- د.محمد بن سعود العصيمي: ~160 companies
- تنمية للاستثمار: ~209 companies
- البلاد المالية: ~238 companies
- **Total**: ~850 companies

### NOMU Market (السوق الموازية)
- الراجحي المالية: ~120 companies
- د.محمد بن سعود العصيمي: ~92 companies (with purification amounts)
- تنمية للاستثمار: ~20 companies
- البلاد المالية: ~111 companies
- **Total**: ~343 companies

## 🛠️ Troubleshooting

### Common Issues

1. **ChromeDriver Issues on Apple Silicon**
   ```bash
   # Install via Homebrew
   brew install chromedriver
   
   # Remove quarantine
   xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
   ```

2. **Module Import Errors**
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   
   # Or use minimal requirements
   pip install -r requirements-minimal.txt
   ```

3. **Permission Errors**
   ```bash
   # Ensure directories exist
   mkdir -p data/exports data/raw data/processed logs
   ```

## 📝 Configuration

Edit `config.py` to customize:

- Shariah institution mappings
- Market classifications
- Export directories
- API settings
- Logging levels
- Update intervals

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is for educational purposes. Please respect Argaam's terms of service when using this scraper.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Users should:
- Respect Argaam's robots.txt and terms of service
- Not overload their servers with excessive requests
- Use the data responsibly and in accordance with applicable laws

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---
*Last updated: August 2025*