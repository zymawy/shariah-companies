# Product Requirements Document: Argaam Shariah Companies Data Scraper

## 1. Project Overview

### Project Name
Argaam Shariah-Compliant Companies Data Scraper

### Project Description
This project automates the extraction of financial data for Shariah-compliant companies from Argaam.com. The system will scrape company information, categorize them by market (تاسي/نمو) and Shariah board (الراجحي/المقاصد), and provide structured data in multiple formats.

### Business Context
Argaam.com provides comprehensive financial data for Saudi listed companies, including Shariah compliance status. This data is valuable for Islamic finance research, investment analysis, and compliance monitoring.

## 2. Objectives

### Primary Objectives
1. Scrape all Shariah-compliant companies from Argaam
2. Categorize companies by market type (TASI/Nomu)
3. Group companies by Shariah certification body
4. Extract key financial metrics and compliance status
5. Provide data in multiple formats for analysis

### Secondary Objectives
1. Track changes in Shariah compliance status
2. Monitor new listings and delistings
3. Create automated update mechanism
4. Generate compliance reports

## 3. Target URL Structure

### Base URL
```
https://www.argaam.com/ar/company/shariahcompanies/1/4/3
```

### URL Parameters Analysis
- `/ar/` - Arabic language
- `/company/shariahcompanies/` - Shariah companies section
- `/1/4/3` - Pagination or filter parameters

## 4. Data Structure

### Company Information
```json
{
  "company_id": "9510",
  "company_name": "الشركة الوطنية للبناء والتسويق",
  "ticker_symbol": "9510",
  "market": "تاسي", // or "نمو"
  "shariah_board": "الراجحي المالية",
  "listing_status": "active",
  "sector": "العقار",
  "subsector": "إدارة وتطوير العقارات"
}
```

### Shariah Boards to Track
1. **الراجحي المالية** (Al Rajhi Capital)
2. **المقاصد** (Al Maqased)
3. **شركة أمواج الدولية** (Amwaj International)
4. **شركة كثير الدولية** (Katheer International)
5. **شركة عبدالعزيز ومحمد ومنصور إبراهيم البابطين**
6. **شركة صناعة البلاستيك العربية**
7. **شركة برج المعرفة التجارية**
8. **شركة لين الخير للتجارة**
9. **شركة بلدي للدواجن**

## 5. Technical Requirements

### Core Technologies
- **Language**: Python 3.8+
- **Web Scraping**: Selenium (for dynamic content), BeautifulSoup4
- **Data Processing**: pandas, numpy
- **Storage**: JSON, CSV, Excel, SQLite
- **Scheduling**: APScheduler or cron
- **API**: FastAPI (optional for data access)

### Required Libraries
```txt
selenium==4.15.2
beautifulsoup4==4.12.2
pandas==2.1.4
numpy==1.26.2
requests==2.31.0
lxml==4.9.3
openpyxl==3.1.2
xlsxwriter==3.1.9
sqlalchemy==2.0.23
fastapi==0.104.1
uvicorn==0.24.0
schedule==1.2.0
arabic-reshaper==3.0.0
python-bidi==0.4.2
```

## 6. Functional Requirements

### 6.1 Web Scraping Module

**Features**:
- Navigate through all pages of Shariah companies
- Handle dynamic content loading
- Extract company details from tables
- Capture market classification
- Identify Shariah board certification

**Data Points to Extract**:
- Company ID/Code
- Company Name (Arabic & English if available)
- Ticker Symbol
- Market (تاسي/نمو)
- Shariah Board
- Sector
- Sub-sector
- Listing Date
- Market Cap (if available)
- Trading Status

### 6.2 Data Classification Module

**Primary Classification**: Market Type
- **تاسي** (TASI - Main Market)
- **نمو** (Nomu - Parallel Market)

**Secondary Classification**: Shariah Board
- Group companies by certifying body
- Track multiple certifications if applicable

### 6.3 Data Processing Module

**Functions**:
- Clean and normalize company names
- Standardize sector classifications
- Handle Arabic text properly
- Validate data integrity
- Remove duplicates
- Track changes over time

### 6.4 Export Module

**Output Formats**:
1. **JSON**: Hierarchical structure by market and board
2. **CSV**: Flat structure for analysis
3. **Excel**: Multiple sheets by classification
4. **SQLite**: Relational database for queries
5. **API**: RESTful endpoints for data access

## 7. Directory Structure

```
argaam-shariah-scraper/
├── README.md
├── requirements.txt
├── .env.example
├── config.py
├── src/
│   ├── __init__.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── argaam_scraper.py
│   │   ├── page_navigator.py
│   │   └── data_extractor.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── classifier.py
│   │   ├── normalizer.py
│   │   └── validator.py
│   ├── exporters/
│   │   ├── __init__.py
│   │   ├── json_exporter.py
│   │   ├── csv_exporter.py
│   │   ├── excel_exporter.py
│   │   └── db_exporter.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── routes.py
│   └── utils/
│       ├── __init__.py
│       ├── arabic_utils.py
│       └── logger.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── exports/
├── logs/
├── tests/
└── scripts/
    ├── run_scraper.py
    └── update_data.py
```

## 8. Data Schema

### Companies Table
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    company_code VARCHAR(10) UNIQUE,
    name_ar VARCHAR(255),
    name_en VARCHAR(255),
    ticker VARCHAR(10),
    market VARCHAR(20),
    shariah_board VARCHAR(255),
    sector VARCHAR(100),
    subsector VARCHAR(100),
    listing_date DATE,
    last_updated TIMESTAMP,
    is_active BOOLEAN
);
```

### Shariah Boards Table
```sql
CREATE TABLE shariah_boards (
    id INTEGER PRIMARY KEY,
    name_ar VARCHAR(255),
    name_en VARCHAR(255),
    company_count INTEGER,
    last_updated TIMESTAMP
);
```

## 9. API Endpoints

### Get All Companies
```
GET /api/v1/companies
Query Parameters:
- market: تاسي|نمو
- board: shariah_board_name
- sector: sector_name
```

### Get Company by ID
```
GET /api/v1/companies/{company_id}
```

### Get Market Summary
```
GET /api/v1/markets/summary
Response:
{
  "تاسي": {
    "total_companies": 150,
    "by_board": {...}
  },
  "نمو": {
    "total_companies": 20,
    "by_board": {...}
  }
}
```

### Get Shariah Board Summary
```
GET /api/v1/boards/{board_name}/companies
```

## 10. Implementation Phases

### Phase 1: Basic Scraper (Day 1-2)
- Setup Selenium WebDriver
- Implement page navigation
- Extract basic company data
- Handle pagination

### Phase 2: Data Processing (Day 3)
- Implement classification logic
- Arabic text processing
- Data validation
- Duplicate handling

### Phase 3: Export Functionality (Day 4)
- JSON export with hierarchy
- CSV/Excel generation
- Database schema and export
- Basic reporting

### Phase 4: API Development (Day 5)
- FastAPI setup
- Implement endpoints
- Documentation
- Testing

### Phase 5: Automation (Day 6)
- Scheduled updates
- Change detection
- Notification system
- Deployment

## 11. Sample Output Structure

### JSON Format
```json
{
  "extraction_date": "2024-01-20T10:00:00",
  "total_companies": 170,
  "markets": {
    "تاسي": {
      "total": 150,
      "by_shariah_board": {
        "الراجحي المالية": [
          {
            "id": "9510",
            "name": "الشركة الوطنية للبناء والتسويق",
            "sector": "العقار"
          }
        ],
        "المقاصد": [...]
      }
    },
    "نمو": {
      "total": 20,
      "by_shariah_board": {...}
    }
  }
}
```

## 12. Error Handling

### Common Issues
1. **Dynamic Content Loading**: Use explicit waits
2. **Session Timeouts**: Implement retry logic
3. **Rate Limiting**: Add delays between requests
4. **Arabic Encoding**: Ensure UTF-8 throughout
5. **Page Structure Changes**: Flexible selectors

## 13. Performance Requirements

- Complete scrape in under 10 minutes
- Handle 500+ companies
- Update detection within 5 seconds per company
- API response time < 100ms
- Support concurrent API requests

## 14. Success Criteria

1. Successfully scrape 100% of listed companies
2. Accurate market classification
3. Correct Shariah board attribution
4. All export formats working
5. API serving data reliably
6. Automated updates functioning
7. Change tracking operational

## 15. Future Enhancements

1. Historical data tracking
2. Financial metrics integration
3. Compliance change alerts
4. Mobile app integration
5. Advanced analytics dashboard
6. Multi-language support
7. Integration with other Islamic finance databases