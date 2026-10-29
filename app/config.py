import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

def normalize_database_url(raw_url):
    """Normalizes database URLs for PostgreSQL (Render/Heroku) and MySQL compatibility."""
    if not raw_url:
        return f"sqlite:///{BASE_DIR / 'fitstart.db'}"
    
    url = raw_url.strip()
    # Normalize Render / Heroku postgresql url
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif url.startswith('postgresql://') and not url.startswith('postgresql+'):
        url = url.replace('postgresql://', 'postgresql+psycopg://', 1)
    elif url.startswith('mysql://'):
        url = url.replace('mysql://', 'mysql+pymysql://', 1)
    
    return url

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fitstart-dev-secret-key-fallback')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = normalize_database_url(os.environ.get('DATABASE_URL'))
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 86400 * 14  # 14 days

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-fitstart'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
