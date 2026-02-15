"""
ドキュメント関連のPydanticスキーマ
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentCreate(BaseModel):
    """ドキュメント作成用スキーマ"""
    title: str = Field(..., min_length=1, max_length=255, description="ドキュメントタイトル")
    content: str = Field(..., min_length=1, max_length=1_000_000, description="ドキュメント本文（最大1MB）")


class DocumentUpdate(BaseModel):
    """ドキュメント更新用スキーマ"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1, max_length=1_000_000)


class DocumentResponse(BaseModel):
    """ドキュメントレスポンス用スキーマ"""
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListItem(BaseModel):
    """ドキュメント一覧用スキーマ（contentは含めない）"""
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True