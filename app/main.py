from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from app.core.deps import get_db
from app.config import settings
from app.api import auth  # 追加：認証用のルーターを読み込む
from app.api import documents  
from app.api import search
from app.models import Base  # 追加：全モデルのベース

app = FastAPI(
    title="RAG Knowledge API",
    description="RAG搭載ナレッジベースAPI",
    version="1.0.0",
)

# 起動時にテーブルを自動作成
@app.on_event("startup")
async def startup_event():
    """アプリ起動時にテーブルを自動作成"""
    try:
        engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")

# ポートバインディング確認用エンドポイント
@app.get("/port-test")
async def port_test():
    """ポートが正しくバインドされているか確認"""
    return {"message": "Port binding successful", "status": "ok"}

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://rag-knowledge-api.onrender.com",
        "https://rag-knowledge-frontend.vercel.app",
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

# Render Python Runtime対応：if __name__ == "__main__" の外に出す
import os
port = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    
    # メモリ節約のための最適化
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Render対応
        port=port,
        reload=False,  # 本番ではreloadなしでメモリ節約
        workers=1,    # ワーカー数を制限
        limit_concurrency=5,  # 同時接続をさらに制限
        timeout_keep_alive=5   # キープアライブ短縮
    )