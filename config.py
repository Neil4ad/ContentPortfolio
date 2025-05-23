# config.py - CORRECTED By NEIL
import os
from datetime import timedelta

def get_database_uri():
    """Get database URI that works in different environments"""
    if os.environ.get('DATABASE_URL'):
        return os.environ.get('DATABASE_URL')
    
    # Try instance folder first (preferred)
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    try:
        os.makedirs(instance_path, exist_ok=True)
        test_file = os.path.join(instance_path, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return f'sqlite:///{os.path.join(instance_path, "portfolio.db")}'
    except (OSError, PermissionError):
        # Fallback to project root if instance folder fails
        return f'sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), "portfolio.db")}'

class Config:
    """Base configuration class"""
    
    # Secret key for sessions and CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Database settings - Portable path that works on all systems
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Admin settings - ADDED missing config variables
    DEFAULT_ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    DEFAULT_ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    DEFAULT_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'changeme123'
    
    # Contact email for form submissions
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL') or 'contact@example.com'
    
    # Mail settings (for contact form notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@example.com'
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Use environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-must-set-a-secret-key-in-production'
    
    def __init__(self):
        if self.SECRET_KEY == 'you-must-set-a-secret-key-in-production':
            raise ValueError("You must set a SECRET_KEY environment variable in production!")

# Configuration dictionary for Flask app
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}