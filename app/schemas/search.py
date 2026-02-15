"""
検索関連のPydanticスキーマ
"""
from pydantic import BaseModel, Field
from typing import List


class SearchRequest(BaseModel):
    """検索リクエスト"""
    query: str = Field(..., min_length=1, max_length=1000, description="検索クエリ")
    top_k: int = Field(default=3, ge=1, le=10, description="返す関連ドキュメント数（1-10）")


class SearchSource(BaseModel):
    """検索ソース（参照元ドキュメント）"""
    document_id: int
    title: str
    content: str
    distance: float = Field(description="類似度距離（小さいほど類似）")


class SearchResponse(BaseModel):
    """検索レスポンス"""
    query: str
    answer: str
    sources: List[SearchSource]