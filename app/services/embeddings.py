"""
埋め込み生成サービス
Jina AI API対応で高速・低メモリ化
"""
from typing import List
import numpy as np
import os
import requests
from app.config import settings

class EmbeddingService:
    def __init__(self, model_name: str = "jina-embeddings-v3"):
        """
        Jina AI APIで初期化
        """
        self.model_name = model_name
        self.api_key = settings.JINA_API_KEY
        self.dimension = 1024  # Jina v3の次元数

    def _load_model(self):
        """Jina APIはロード不要"""
        return True

    def embed_text(self, text: str) -> np.ndarray:
        """単一テキストの埋め込み生成"""
        return self._embed_with_jina([text])[0]

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """複数テキストの埋め込み生成"""
        return self._embed_with_jina(texts)

    def _embed_with_jina(self, texts: List[str]) -> np.ndarray:
        """Jina APIで埋め込み生成"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model_name,
            "input": texts
        }
        
        try:
            response = requests.post(
                "https://api.jina.ai/v1/embeddings",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                embeddings = [item["embedding"] for item in response.json()["data"]]
                return np.array(embeddings, dtype=np.float32)
            else:
                raise Exception(f"Jina API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Jina API error: {e}")
            raise

def get_embedding_service() -> EmbeddingService:
    """埋め込みサービスのインスタンスを取得"""
    return EmbeddingService()
