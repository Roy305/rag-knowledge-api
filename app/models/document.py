"""
ドキュメントモデル

ユーザーがアップロードしたドキュメントを管理
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimestampModel


class Document(TimestampModel):
    """
    ドキュメントモデル
    
    ユーザーごとにドキュメントを管理
    RAG検索の対象データ
    """
    __tablename__ = "documents"
    
    # id, created_at, updated_at は TimestampModel から継承
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # リレーション（Userモデルとの関連）
    user = relationship("User", back_populates="documents")