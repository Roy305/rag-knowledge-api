"""
埋め込み生成サービス
sentence-transformersを使ってテキストをベクトル化
"""
from typing import List
import numpy as np

# ここで import せず、使うときまで後回しにする

class EmbeddingService:
    def __init__(self, model_name: str = "oshizo/sbert-jsnli-l6-h384-aligned"):
        """
        初期化
        """
        self.model_name = model_name
        self.model = None  # 起動時は空にしておく
        self.dimension = 384  # このモデルの固定次元数

    def _load_model(self):
        """モデルが必要になった瞬間に初めてロードする"""
        if self.model is None:
            print("🚀 Loading SentenceTransformer model (Lazy Load)...")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        return self.model
    
    def embed_text(self, text: str) -> np.ndarray:
        model = self._load_model()
        return model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        model = self._load_model()
        return model.encode(texts, convert_to_numpy=True)


# グローバルインスタンス
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        # ここではクラスを作るだけで、モデルのロードはまだしない
        _embedding_service = EmbeddingService()
    return _embedding_service