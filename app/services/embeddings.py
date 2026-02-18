"""
埋め込み生成サービス

sentence-transformersを使ってテキストをベクトル化
"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


# 中略 ...

class EmbeddingService:
    def __init__(self, model_name: str = "oshizo/sbert-jsnli-l6-h384-aligned"):
        """
        初期化
        モデルを軽量な日本語対応モデルに変更
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

# 中略 ...entence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        単一テキストの埋め込み生成
        
        Args:
            text: 埋め込み対象のテキスト
            
        Returns:
            埋め込みベクトル（numpy配列）
        """
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        複数テキストの埋め込み生成（バッチ処理）
        
        Args:
            texts: 埋め込み対象のテキストリスト
            
        Returns:
            埋め込みベクトルの配列
        """
        return self.model.encode(texts, convert_to_numpy=True)


# グローバルインスタンス（起動時に1回だけ初期化）
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """
    埋め込みサービスのシングルトンインスタンスを取得
    
    モデルの読み込みは重いので、1回だけ初期化する
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service