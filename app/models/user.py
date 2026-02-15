from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship  # ← 追加
from app.models.base import TimestampModel


class User(TimestampModel):
    """
    ユーザーモデル
    JWT認証用のユーザー情報を管理します。
    """
    __tablename__ = "users"
    
    # id, created_at, updated_at は TimestampModel(base.py) から継承
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # リレーション（Documentモデルとの関連）
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")  # ← 追加