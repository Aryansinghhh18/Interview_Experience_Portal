import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-insecure-secret-key-replace-in-production")
    
    # Database Settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "interview_experience_portal")
    USE_SQLITE_FALLBACK = os.getenv("USE_SQLITE_FALLBACK", "true").lower() in ("true", "1", "yes")
    SQLITE_DB_PATH = BASE_DIR / "interview_portal.db"
    
    # AI Provider Settings
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Vector Search
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    FAISS_INDEX_PATH = BASE_DIR / "vector_index.faiss"
    FAISS_METADATA_PATH = BASE_DIR / "vector_metadata.json"
    
    # Upload Settings
    UPLOAD_FOLDER = BASE_DIR / "uploads" / "resumes"
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024)) # 10 MB
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    
    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    WTF_CSRF_TIME_LIMIT = 7200
