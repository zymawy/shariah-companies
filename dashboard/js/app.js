// ========================================
// Global Variables
// ========================================
let companiesData = [];
let chartsInitialized = false;
let language = 'ar';
let theme = 'light';

// GitHub Repository Information
const GITHUB_REPO = 'zymawy/almaqased';
const GITHUB_BRANCH = 'main';
const DATA_PATH = 'data/exports';

// ========================================
// Initialize Application
// ========================================
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Initializing Shariah Companies Dashboard...');
    
    // Initialize theme
    initializeTheme();
    
    // Load data from GitHub
    await loadDataFromGitHub();
    
    // Initialize components
    initializeStatistics();
    initializeCharts();
    initializeDataTable();
    initializeFilters();
    initializeEventListeners();
    
    // Hide loading screen
    setTimeout(() => {
        document.getElementById('loadingScreen').classList.add('hidden');
    }, 1000);
    
    // Update last update time
    updateLastUpdateTime();
    
    // Add smooth scroll
    initializeSmoothScroll();
});

// ========================================
// Data Loading from GitHub
// ========================================
async function loadDataFromGitHub() {
    try {
        console.log('Fetching data from GitHub...');
        
        // Try to fetch the most recent JSON file from the repository
        const dataFiles = [
            `https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/${DATA_PATH}/companies_flat_latest.json`,
            `https://raw.githubusercontent.com/${GITHUB_REPO}/${GITHUB_BRANCH}/${DATA_PATH}/sample_data.json`,
            // Fallback to local sample data
            './data/sample_data.json'
        ];
        
        let dataLoaded = false;
        
        for (const url of dataFiles) {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    companiesData = await response.json();
                    console.log(`Successfully loaded data from: ${url}`);
                    console.log(`Total companies loaded: ${companiesData.length}`);
                    dataLoaded = true;
                    break;
                }
            } catch (error) {
                console.log(`Failed to load from ${url}, trying next source...`);
            }
        }
        
        // If no data loaded from GitHub, use sample data
        if (!dataLoaded) {
            console.log('Using sample data...');
            companiesData = generateSampleData();
        }
        
    } catch (error) {
        console.error('Error loading data:', error);
        // Use sample data as fallback
        companiesData = generateSampleData();
    }
}

// ========================================
// Generate Sample Data (Fallback)
// ========================================
function generateSampleData() {
    const boards = ['الراجحي المالية', 'د.محمد بن سعود العصيمي', 'تنمية للاستثمار', 'البلاد المالية'];
    const markets = ['تاسي', 'نمو'];
    const sectors = ['البنوك', 'الصناعة', 'العقار', 'التجزئة', 'الاتصالات', 'التأمين', 'الطاقة', 'الزراعة'];
    
    const sampleData = [];
    const companyCounts = {
        'الراجحي المالية': { 'تاسي': 243, 'نمو': 120 },
        'د.محمد بن سعود العصيمي': { 'تاسي': 160, 'نمو': 92 },
        'تنمية للاستثمار': { 'تاسي': 209, 'نمو': 20 },
        'البلاد المالية': { 'تاسي': 238, 'نمو': 111 }
    };
    
    let companyCode = 1000;
    
    for (const board of boards) {
        for (const market of markets) {
            const count = companyCounts[board][market];
            for (let i = 0; i < count; i++) {
                companyCode++;
                sampleData.push({
                    company_code: companyCode.toString(),
                    company_name: `شركة ${market} ${board} ${i + 1}`,
                    ticker_symbol: companyCode.toString(),
                    market: market,
                    shariah_board: board,
                    sector: sectors[Math.floor(Math.random() * sectors.length)],
                    subsector: '',
                    classification: 'شرعي',
                    purification_amount: board === 'د.محمد بن سعود العصيمي' && market === 'نمو' ? 
                        (Math.random() * 0.15).toFixed(2) : null,
                    timestamp: new Date().toISOString()
                });
            }
        }
    }
    
    return sampleData;
}

// ========================================
// Initialize Statistics
// ========================================
function initializeStatistics() {
    const stats = calculateStatistics();
    
    // Animate counters
    animateCounter('totalCompanies', stats.total);
    animateCounter('tasiCompanies', stats.tasi);
    animateCounter('nomuCompanies', stats.nomu);
    animateCounter('totalBoards', 4);
}

function calculateStatistics() {
    const total = companiesData.length;
    const tasi = companiesData.filter(c => c.market === 'تاسي').length;
    const nomu = companiesData.filter(c => c.market === 'نمو').length;
    
    return { total, tasi, nomu };
}

function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    const duration = 2000;
    const start = 0;
    const increment = targetValue / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= targetValue) {
            element.textContent = targetValue.toLocaleString('ar-SA');
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString('ar-SA');
        }
    }, 16);
}

// ========================================
// Initialize Charts
// ========================================
function initializeCharts() {
    // Set Chart.js defaults for RTL
    Chart.defaults.font.family = 'Tajawal';
    Chart.defaults.plugins.legend.rtl = true;
    Chart.defaults.plugins.tooltip.rtl = true;
    
    // Create all charts
    createBoardDistributionChart();
    createMarketPieChart();
    createTasiChart();
    createNomuChart();
    createBoardComparisonChart();
    
    chartsInitialized = true;
}

function createBoardDistributionChart() {
    const ctx = document.getElementById('boardDistributionChart').getContext('2d');
    const boardData = {};
    
    companiesData.forEach(company => {
        if (!boardData[company.shariah_board]) {
            boardData[company.shariah_board] = { tasi: 0, nomu: 0 };
        }
        if (company.market === 'تاسي') {
            boardData[company.shariah_board].tasi++;
        } else {
            boardData[company.shariah_board].nomu++;
        }
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(boardData),
            datasets: [{
                label: 'السوق الرئيسية (تاسي)',
                data: Object.values(boardData).map(d => d.tasi),
                backgroundColor: 'rgba(44, 122, 123, 0.8)',
                borderColor: 'rgba(44, 122, 123, 1)',
                borderWidth: 2
            }, {
                label: 'السوق الموازية (نمو)',
                data: Object.values(boardData).map(d => d.nomu),
                backgroundColor: 'rgba(237, 137, 54, 0.8)',
                borderColor: 'rgba(237, 137, 54, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + ' شركة';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function createMarketPieChart() {
    const ctx = document.getElementById('marketPieChart').getContext('2d');
    const stats = calculateStatistics();
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['السوق الرئيسية (تاسي)', 'السوق الموازية (نمو)'],
            datasets: [{
                data: [stats.tasi, stats.nomu],
                backgroundColor: [
                    'rgba(44, 122, 123, 0.8)',
                    'rgba(237, 137, 54, 0.8)'
                ],
                borderColor: [
                    'rgba(44, 122, 123, 1)',
                    'rgba(237, 137, 54, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' شركة (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

function createTasiChart() {
    const ctx = document.getElementById('tasiChart').getContext('2d');
    const tasiCompanies = companiesData.filter(c => c.market === 'تاسي');
    const sectorData = {};
    
    tasiCompanies.forEach(company => {
        sectorData[company.sector] = (sectorData[company.sector] || 0) + 1;
    });
    
    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: Object.keys(sectorData),
            datasets: [{
                label: 'عدد الشركات',
                data: Object.values(sectorData),
                backgroundColor: 'rgba(44, 122, 123, 0.2)',
                borderColor: 'rgba(44, 122, 123, 1)',
                borderWidth: 2,
                pointBackgroundColor: 'rgba(44, 122, 123, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(44, 122, 123, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    pointLabels: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function createNomuChart() {
    const ctx = document.getElementById('nomuChart').getContext('2d');
    const nomuCompanies = companiesData.filter(c => c.market === 'نمو');
    const boardData = {};
    
    nomuCompanies.forEach(company => {
        boardData[company.shariah_board] = (boardData[company.shariah_board] || 0) + 1;
    });
    
    new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: Object.keys(boardData),
            datasets: [{
                data: Object.values(boardData),
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(237, 137, 54, 0.8)',
                    'rgba(72, 187, 120, 0.8)',
                    'rgba(245, 101, 101, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

function createBoardComparisonChart() {
    const ctx = document.getElementById('boardComparisonChart').getContext('2d');
    const boards = ['الراجحي المالية', 'د.محمد بن سعود العصيمي', 'تنمية للاستثمار', 'البلاد المالية'];
    const sectors = [...new Set(companiesData.map(c => c.sector))];
    
    const datasets = boards.map((board, index) => {
        const boardCompanies = companiesData.filter(c => c.shariah_board === board);
        const sectorCounts = sectors.map(sector => 
            boardCompanies.filter(c => c.sector === sector).length
        );
        
        const colors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(72, 187, 120, 0.8)',
            'rgba(237, 137, 54, 0.8)',
            'rgba(245, 101, 101, 0.8)'
        ];
        
        return {
            label: board,
            data: sectorCounts,
            backgroundColor: colors[index],
            borderColor: colors[index].replace('0.8', '1'),
            borderWidth: 2
        };
    });
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sectors,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        font: {
                            size: 13
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: false
                },
                x: {
                    stacked: false
                }
            }
        }
    });
}

// ========================================
// Initialize DataTable
// ========================================
function initializeDataTable() {
    const tableBody = document.getElementById('companiesTableBody');
    tableBody.innerHTML = '';
    
    companiesData.forEach((company, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${company.company_code}</td>
            <td>${company.company_name}</td>
            <td><span class="badge bg-${company.market === 'تاسي' ? 'info' : 'warning'}">${company.market}</span></td>
            <td>${company.shariah_board}</td>
            <td>${company.sector || '-'}</td>
            <td>${company.purification_amount ? company.purification_amount + ' ريال' : '-'}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="showCompanyDetails(${index})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Initialize DataTable
    if ($.fn.DataTable.isDataTable('#companiesTable')) {
        $('#companiesTable').DataTable().destroy();
    }
    
    $('#companiesTable').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/ar.json'
        },
        pageLength: 25,
        responsive: true,
        order: [[0, 'asc']],
        dom: 'Bfrtip',
        buttons: ['copy', 'csv', 'excel', 'pdf', 'print']
    });
}

// ========================================
// Initialize Filters
// ========================================
function initializeFilters() {
    // Populate sector filter
    const sectors = [...new Set(companiesData.map(c => c.sector).filter(s => s))];
    const sectorFilter = document.getElementById('sectorFilter');
    
    sectors.forEach(sector => {
        const option = document.createElement('option');
        option.value = sector;
        option.textContent = sector;
        sectorFilter.appendChild(option);
    });
    
    // Add filter event listeners
    document.getElementById('marketFilter').addEventListener('change', applyFilters);
    document.getElementById('boardFilter').addEventListener('change', applyFilters);
    document.getElementById('sectorFilter').addEventListener('change', applyFilters);
    document.getElementById('searchInput').addEventListener('input', applyFilters);
}

function applyFilters() {
    const marketFilter = document.getElementById('marketFilter').value;
    const boardFilter = document.getElementById('boardFilter').value;
    const sectorFilter = document.getElementById('sectorFilter').value;
    const searchFilter = document.getElementById('searchInput').value.toLowerCase();
    
    let filteredData = companiesData;
    
    if (marketFilter) {
        filteredData = filteredData.filter(c => c.market === marketFilter);
    }
    
    if (boardFilter) {
        filteredData = filteredData.filter(c => c.shariah_board === boardFilter);
    }
    
    if (sectorFilter) {
        filteredData = filteredData.filter(c => c.sector === sectorFilter);
    }
    
    if (searchFilter) {
        filteredData = filteredData.filter(c => 
            c.company_name.toLowerCase().includes(searchFilter) ||
            c.company_code.includes(searchFilter)
        );
    }
    
    // Update table
    updateTable(filteredData);
}

function updateTable(data) {
    const tableBody = document.getElementById('companiesTableBody');
    tableBody.innerHTML = '';
    
    data.forEach((company, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${company.company_code}</td>
            <td>${company.company_name}</td>
            <td><span class="badge bg-${company.market === 'تاسي' ? 'info' : 'warning'}">${company.market}</span></td>
            <td>${company.shariah_board}</td>
            <td>${company.sector || '-'}</td>
            <td>${company.purification_amount ? company.purification_amount + ' ريال' : '-'}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="showCompanyDetails(${index})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

// ========================================
// Company Details Modal
// ========================================
function showCompanyDetails(index) {
    const company = companiesData[index];
    const modalTitle = document.getElementById('companyModalTitle');
    const modalBody = document.getElementById('companyModalBody');
    
    modalTitle.textContent = company.company_name;
    
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <p><strong>رمز الشركة:</strong> ${company.company_code}</p>
                <p><strong>السوق:</strong> <span class="badge bg-${company.market === 'تاسي' ? 'info' : 'warning'}">${company.market}</span></p>
                <p><strong>القطاع:</strong> ${company.sector || '-'}</p>
            </div>
            <div class="col-md-6">
                <p><strong>الهيئة الشرعية:</strong> ${company.shariah_board}</p>
                <p><strong>التصنيف:</strong> ${company.classification}</p>
                <p><strong>مبلغ التطهير:</strong> ${company.purification_amount ? company.purification_amount + ' ريال' : 'غير متاح'}</p>
            </div>
        </div>
        <hr>
        <div class="mt-3">
            <h6>معلومات إضافية</h6>
            <p class="text-muted">آخر تحديث: ${new Date(company.timestamp).toLocaleDateString('ar-SA')}</p>
        </div>
    `;
    
    const modal = new bootstrap.Modal(document.getElementById('companyModal'));
    modal.show();
}

// ========================================
// Initialize Event Listeners
// ========================================
function initializeEventListeners() {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    
    // Language toggle
    document.getElementById('langToggle').addEventListener('click', toggleLanguage);
    
    // Smooth scroll for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ========================================
// Theme Management
// ========================================
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    theme = savedTheme;
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon();
}

function toggleTheme() {
    theme = theme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = document.querySelector('#themeToggle i');
    icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
}

// ========================================
// Language Management
// ========================================
function toggleLanguage() {
    language = language === 'ar' ? 'en' : 'ar';
    document.documentElement.setAttribute('lang', language);
    document.documentElement.setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
    document.getElementById('langToggle').textContent = language === 'ar' ? 'EN' : 'عربي';
    
    // Reload charts with new language
    if (chartsInitialized) {
        // Charts will need to be reinitialized with new labels
        location.reload();
    }
}

// ========================================
// Utility Functions
// ========================================
function updateLastUpdateTime() {
    const lastUpdate = document.getElementById('lastUpdate');
    const now = new Date();
    lastUpdate.textContent = now.toLocaleDateString('ar-SA') + ' ' + now.toLocaleTimeString('ar-SA');
}

function initializeSmoothScroll() {
    // Add smooth scrolling to all internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ========================================
// Export Functions (Global)
// ========================================
window.showCompanyDetails = showCompanyDetails;