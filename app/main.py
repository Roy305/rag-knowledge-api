from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.deps import get_db
from app.config import settings
from app.api import auth  # ✅ 追加：認証用のルーターを読み込む
from app.api import documents  
from app.api import search

app = FastAPI(
    title="RAG Knowledge API",
    description="RAG搭載ナレッジベースAPI",
    version="1.0.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://rag-knowledge-api.onrender.com",
        "https://rag-knowledge-frontend-q9bo.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ルーターの登録
# ✅ これを呼ぶことで /auth/register や /auth/login が使えるようになるよ
app.include_router(auth.router)
app.include_router(documents.router) 
app.include_router(search.router)

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """
    アプリとDBの生存確認用エンドポイント（Day 1の豪華版を維持）
    """
    try:
        # DB接続確認
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "database": "connected"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500