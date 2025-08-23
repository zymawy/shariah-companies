"""
Database models for Shariah companies data
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

Base = declarative_base()

class Company(Base):
    """Company model"""
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_code = Column(String(20), unique=True, nullable=False)
    ticker_symbol = Column(String(20))
    name_ar = Column(String(255), nullable=False)
    name_en = Column(String(255))
    market = Column(String(50), nullable=False)
    shariah_board_id = Column(Integer, ForeignKey('shariah_boards.id'))
    sector = Column(String(100))
    subsector = Column(String(100))
    classification = Column(String(50), default='شرعي')
    listing_date = Column(DateTime)
    market_cap = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    shariah_board = relationship("ShariahBoard", back_populates="companies")
    historical_data = relationship("CompanyHistory", back_populates="company")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'company_code': self.company_code,
            'ticker_symbol': self.ticker_symbol,
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'market': self.market,
            'shariah_board': self.shariah_board.name_ar if self.shariah_board else None,
            'sector': self.sector,
            'subsector': self.subsector,
            'classification': self.classification,
            'is_active': self.is_active,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ShariahBoard(Base):
    """Shariah Board model"""
    __tablename__ = 'shariah_boards'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name_ar = Column(String(255), unique=True, nullable=False)
    name_en = Column(String(255))
    description = Column(Text)
    website = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    companies = relationship("Company", back_populates="shariah_board")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name_ar': self.name_ar,
            'name_en': self.name_en,
            'description': self.description,
            'website': self.website,
            'company_count': len(self.companies),
            'is_active': self.is_active
        }

class CompanyHistory(Base):
    """Historical data for companies"""
    __tablename__ = 'company_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    snapshot_date = Column(DateTime, nullable=False)
    market = Column(String(50))
    shariah_board = Column(String(255))
    sector = Column(String(100))
    classification = Column(String(50))
    market_cap = Column(Float)
    change_type = Column(String(50))  # 'new', 'updated', 'delisted'
    change_details = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    company = relationship("Company", back_populates="historical_data")

class ScrapingLog(Base):
    """Log scraping activities"""
    __tablename__ = 'scraping_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_date = Column(DateTime, nullable=False)
    total_companies = Column(Integer)
    new_companies = Column(Integer)
    updated_companies = Column(Integer)
    deleted_companies = Column(Integer)
    duration_seconds = Column(Integer)
    status = Column(String(50))  # 'success', 'partial', 'failed'
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# Database manager class
class DatabaseManager:
    """Database manager for CRUD operations"""
    
    def __init__(self, database_url=None):
        """Initialize database connection"""
        self.database_url = database_url or config.DATABASE_URL
        self.engine = create_engine(self.database_url, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def close(self):
        """Close database session"""
        self.session.close()
    
    def add_or_update_company(self, company_data):
        """Add or update a company"""
        try:
            # Check if company exists
            existing = self.session.query(Company).filter_by(
                company_code=company_data['company_code']
            ).first()
            
            # Get or create Shariah board
            shariah_board = None
            if company_data.get('shariah_board'):
                shariah_board = self.get_or_create_shariah_board(
                    company_data['shariah_board']
                )
            
            if existing:
                # Update existing company
                changes = []
                if existing.name_ar != company_data.get('company_name'):
                    changes.append(f"Name: {existing.name_ar} -> {company_data.get('company_name')}")
                    existing.name_ar = company_data.get('company_name')
                
                if existing.market != company_data.get('market'):
                    changes.append(f"Market: {existing.market} -> {company_data.get('market')}")
                    existing.market = company_data.get('market')
                
                if shariah_board and existing.shariah_board_id != shariah_board.id:
                    changes.append(f"Shariah Board changed")
                    existing.shariah_board = shariah_board
                
                existing.sector = company_data.get('sector')
                existing.subsector = company_data.get('subsector')
                existing.updated_at = datetime.now()
                
                # Log changes to history
                if changes:
                    self.add_company_history(existing, 'updated', ', '.join(changes))
                
                self.session.commit()
                return existing, 'updated'
            
            else:
                # Create new company
                new_company = Company(
                    company_code=company_data['company_code'],
                    ticker_symbol=company_data.get('ticker_symbol'),
                    name_ar=company_data.get('company_name'),
                    market=company_data.get('market'),
                    shariah_board=shariah_board,
                    sector=company_data.get('sector'),
                    subsector=company_data.get('subsector'),
                    classification=company_data.get('classification', 'شرعي')
                )
                
                self.session.add(new_company)
                self.session.commit()
                
                # Log to history
                self.add_company_history(new_company, 'new', 'New company added')
                
                return new_company, 'created'
                
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_or_create_shariah_board(self, name_ar):
        """Get or create a Shariah board"""
        board = self.session.query(ShariahBoard).filter_by(name_ar=name_ar).first()
        
        if not board:
            board = ShariahBoard(name_ar=name_ar)
            self.session.add(board)
            self.session.commit()
        
        return board
    
    def add_company_history(self, company, change_type, change_details):
        """Add company history record"""
        history = CompanyHistory(
            company_id=company.id,
            snapshot_date=datetime.now(),
            market=company.market,
            shariah_board=company.shariah_board.name_ar if company.shariah_board else None,
            sector=company.sector,
            classification=company.classification,
            change_type=change_type,
            change_details=change_details
        )
        
        self.session.add(history)
        self.session.commit()
    
    def log_scraping_activity(self, stats):
        """Log scraping activity"""
        log = ScrapingLog(
            scrape_date=stats['start_time'],
            total_companies=stats['companies_found'],
            new_companies=stats.get('new_companies', 0),
            updated_companies=stats.get('updated_companies', 0),
            deleted_companies=stats.get('deleted_companies', 0),
            duration_seconds=(stats['end_time'] - stats['start_time']).seconds if stats.get('end_time') else 0,
            status='success' if not stats['errors'] else 'partial',
            error_message='; '.join(stats['errors']) if stats['errors'] else None
        )
        
        self.session.add(log)
        self.session.commit()
    
    def get_all_companies(self, market=None, shariah_board=None):
        """Get all companies with optional filters"""
        query = self.session.query(Company).filter_by(is_active=True)
        
        if market:
            query = query.filter_by(market=market)
        
        if shariah_board:
            query = query.join(ShariahBoard).filter(ShariahBoard.name_ar == shariah_board)
        
        return query.all()
    
    def get_company_by_code(self, company_code):
        """Get company by code"""
        return self.session.query(Company).filter_by(company_code=company_code).first()
    
    def get_statistics(self):
        """Get database statistics"""
        total_companies = self.session.query(Company).filter_by(is_active=True).count()
        
        # Count by market
        tasi_count = self.session.query(Company).filter_by(
            is_active=True, 
            market=config.MARKETS['TASI']
        ).count()
        
        nomu_count = self.session.query(Company).filter_by(
            is_active=True,
            market=config.MARKETS['NOMU']
        ).count()
        
        # Count by Shariah board
        boards = self.session.query(ShariahBoard).all()
        board_stats = {}
        for board in boards:
            board_stats[board.name_ar] = len(board.companies)
        
        return {
            'total_companies': total_companies,
            'by_market': {
                config.MARKETS['TASI']: tasi_count,
                config.MARKETS['NOMU']: nomu_count
            },
            'by_shariah_board': board_stats,
            'last_update': self.get_last_scrape_date()
        }
    
    def get_last_scrape_date(self):
        """Get the date of the last successful scrape"""
        last_log = self.session.query(ScrapingLog).filter_by(
            status='success'
        ).order_by(ScrapingLog.scrape_date.desc()).first()
        
        return last_log.scrape_date.isoformat() if last_log else None
    
    def mark_inactive_companies(self, active_codes):
        """Mark companies not in the active list as inactive"""
        all_companies = self.session.query(Company).filter_by(is_active=True).all()
        
        for company in all_companies:
            if company.company_code not in active_codes:
                company.is_active = False
                self.add_company_history(company, 'delisted', 'Company marked as inactive')
        
        self.session.commit()