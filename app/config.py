import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fitstart-dev-secret-key-fallback')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Preferred database is MySQL, falling back to SQLite if MySQL is not running or not configured
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = f"sqlite:///{BASE_DIR / 'fitstart.db'}"
    elif database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = database_url
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

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
