from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# --- 修正ポイント1: URLの頭を postgresql:// に強制変換 ---
# SQLAlchemy 1.4以降、postgres:// (lなし) はエラーになるため
db_url = settings.DATABASE_URL
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Render/Supabase接続用のEngine設定
engine = create_engine(
    db_url, # 修正したURLを使う
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    # --- 修正ポイント2: 接続時に public スキーマを強制指定 ---
    # Session Pooler経由だとたまにスキーマを見失うため
    connect_args={
        "options": "-c search_path=public"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()