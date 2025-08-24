# Shariah Companies Analytics Dashboard | لوحة تحليل الشركات الشرعية

A beautiful, interactive dashboard for analyzing Shariah-compliant companies data from the Saudi stock market (TASI & NOMU).

## 🌟 Features

### Visual Analytics
- **Interactive Charts**: Multiple chart types (Bar, Pie, Radar, Polar Area) for comprehensive data visualization
- **Real-time Statistics**: Animated counters and live data updates
- **Market Comparison**: Side-by-side analysis of TASI and NOMU markets
- **Board Analysis**: Detailed comparison of all 4 Shariah certification boards

### Data Presentation
- **Responsive Tables**: Sortable, searchable, and filterable company listings
- **Advanced Filtering**: Filter by market, Shariah board, sector, or search by name
- **Company Details**: Detailed modal views for each company
- **Purification Amounts**: Display purification amounts when available

### User Experience
- **Mobile-First Design**: Fully responsive across all devices
- **Dark Mode**: Toggle between light and dark themes
- **Bilingual Support**: Arabic (RTL) and English (LTR) support
- **Smooth Animations**: Professional transitions and hover effects
- **Fast Loading**: Optimized performance with lazy loading

## 🚀 Live Demo

Visit the live dashboard at: [https://zymawy.github.io/almaqased/](https://zymawy.github.io/almaqased/)

## 📊 Data Sources

The dashboard fetches data from:
1. **GitHub Repository**: Automatically pulls the latest scraped data from the main repository
2. **Fallback Data**: Uses sample data if GitHub data is unavailable
3. **Daily Updates**: Automated scraping and deployment via GitHub Actions

## 🎨 Technology Stack

- **Frontend Framework**: Pure JavaScript (no framework dependencies)
- **CSS Framework**: Bootstrap 5.3.2
- **Charts**: Chart.js 4.x
- **Tables**: DataTables 1.13.7
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Tajawal)
- **Hosting**: GitHub Pages (100% free)

## 📱 Features by Section

### 1. Overview Section
- Total companies counter
- Market distribution (TASI/NOMU)
- Shariah boards count
- Interactive distribution charts

### 2. Markets Analysis
- TASI market radar chart by sectors
- NOMU market polar area chart
- Market share percentages
- Progress indicators

### 3. Shariah Boards
- Individual board statistics cards
- Company count by market
- Purification amount indicators
- Comparative bar chart

### 4. Companies Table
- Full company listing
- Advanced search and filtering
- Export to CSV/Excel/PDF
- Responsive design

### 5. Comparison Matrix
- Board agreement analysis
- Disputed companies listing
- Venn diagram visualization
- Certification overlap analysis

## 🛠️ Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/zymawy/almaqased.git
cd almaqased/dashboard
```

2. Open in browser:
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server

# Or simply open index.html in your browser
```

### GitHub Pages Deployment

1. Fork the repository
2. Enable GitHub Pages in repository settings
3. Select the `dashboard` folder as the source
4. Access at: `https://[username].github.io/almaqased/`

## 🔄 Data Updates

### Automatic Updates
The dashboard automatically updates daily via GitHub Actions:
- Runs the scraper at midnight UTC
- Updates the data files
- Deploys to GitHub Pages

### Manual Updates
To manually update the data:

1. Run the scraper:
```bash
python main.py --export-format json
```

2. Copy the latest data:
```bash
cp data/exports/companies_flat_*.json dashboard/data/companies_flat_latest.json
```

3. Commit and push:
```bash
git add .
git commit -m "Update dashboard data"
git push
```

## 📂 Project Structure

```
dashboard/
├── index.html          # Main dashboard page
├── css/
│   └── styles.css     # Custom styles and animations
├── js/
│   └── app.js         # Dashboard logic and charts
├── data/
│   ├── sample_data.json           # Sample data for testing
│   └── companies_flat_latest.json # Latest scraped data
└── assets/
    └── icons/         # Custom icons (if needed)
```

## 🎯 Key Features Implementation

### Data Fetching from GitHub
```javascript
// Fetches data directly from GitHub repository
const GITHUB_REPO = 'zymawy/almaqased';
const DATA_URL = `https://raw.githubusercontent.com/${GITHUB_REPO}/main/data/exports/companies_flat_latest.json`;
```

### Responsive Charts
- All charts are fully responsive
- Automatic resizing on viewport changes
- Touch-friendly on mobile devices

### Dark Mode
- System preference detection
- Manual toggle with persistence
- Smooth theme transitions

### Performance Optimizations
- Lazy loading for images
- Debounced search input
- Virtual scrolling for large tables
- Minified assets

## 🌐 Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📈 Analytics Integration

The dashboard can be extended with:
- Google Analytics
- Microsoft Clarity
- Custom event tracking

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This dashboard is part of the Argaam Shariah Companies Scraper project and is for educational purposes.

## 🙏 Acknowledgments

- Data source: Argaam.com
- Charts library: Chart.js
- CSS framework: Bootstrap
- Icons: Font Awesome

## 📧 Contact

For questions or issues, please open an issue on [GitHub](https://github.com/zymawy/almaqased/issues).

---
*Last updated: August 2025*