from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# プロジェクトルートの絶対パス
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # Environment
    ENVIRONMENT: str = "dev"
    
    # Database
    DATABASE_URL: str
    
    # JWT Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # LLM API
    GROQ_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False
    )

settings = Settings()

# デバッグ用出力
print(f"[CONFIG] Loading .env from: {ENV_FILE}")
print(f"[CONFIG] .env exists: {ENV_FILE.exists()}")
if settings.GROQ_API_KEY:
    print(f"[CONFIG] GROQ_API_KEY loaded: {settings.GROQ_API_KEY[:20]}...")
else:
    print("[CONFIG] GROQ_API_KEY: NOT LOADED")