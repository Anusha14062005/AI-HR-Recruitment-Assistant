import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    """Application configuration loaded from environment variables."""
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv('SECRET_KEY', 'ai-hr-recruitment-default-super-secret-key-2025')
    
    # Database Settings (MySQL)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'ai_hr_recruitment')
    
    # AI / LLM Configuration
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'demo').lower()
    AI_API_KEY = os.getenv('AI_API_KEY', '').strip()
    AI_MODEL = os.getenv('AI_MODEL', 'gemini-1.5-flash')
    
    # DEMO_MODE: Default true if set to 'true', '1', 'yes', or if AI_API_KEY is empty
    DEMO_MODE_RAW = os.getenv('DEMO_MODE', 'true').strip().lower()
    DEMO_MODE = DEMO_MODE_RAW in ('true', '1', 'yes', 'on') or not AI_API_KEY
    
    # File Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv('UPLOAD_FOLDER', 'static/uploads/resumes'))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB max limit
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

    @classmethod
    def ensure_upload_dir(cls):
        """Ensure upload folder exists."""
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
