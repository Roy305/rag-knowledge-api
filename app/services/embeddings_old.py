"""
埋め込み生成サービス
ONNX + INT8量子化で高速・低メモリ化
"""
from typing import List
import numpy as np
import os
from pathlib import Path

# ONNXモデルパス
ONNX_MODEL_DIR = Path("onnx_model")

class EmbeddingService:
    def __init__(self, model_name: str = "oshizo/sbert-jsnli-luke-japanese-base-lite"):
        """
        ONNXモデルで初期化
        """
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.dimension = 1024 # SBERTの固定次元数

    def _load_model(self):
        """ONNXモデルが必要になった瞬間に初めてロードする"""
        if self.model is None:
            print(f"🚀 Loading model from {ONNX_MODEL_DIR}")
            
            # ONNXモデルの存在確認
            if ONNX_MODEL_DIR.exists():
                print("🔍 ONNX model found, loading...")
                try:
                    from optimum.onnxruntime import ORTModelForFeatureExtraction
                    from transformers import AutoTokenizer
                    
                    # ONNXモデルとトークナイザー読み込み
                    self.model = ORTModelForFeatureExtraction.from_pretrained(
                        str(ONNX_MODEL_DIR),
                        provider="CPUExecutionProvider"
                    )
                    self.tokenizer = AutoTokenizer.from_pretrained(str(ONNX_MODEL_DIR))
                    print("✅ ONNX model loaded successfully")
                except Exception as e:
                    print(f"❌ ONNX load failed: {e}")
                    print("🔄 Fallback to sentence-transformers...")
                    # ここで一度だけインポート
                    from sentence_transformers import SentenceTransformer
                    self.model = SentenceTransformer(self.model_name)
                    self.tokenizer = None
            else:
                print("⚠️ ONNX model not found, using sentence-transformers")
                # ここで一度だけインポート
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
                self.tokenizer = None
        return self.model
    
    def embed_text(self, text: str) -> np.ndarray:
        """単一テキストの埋め込み生成（ONNX対応）"""
        model = self._load_model()
        
        if self.tokenizer:
            # ONNXモデル使用
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            with torch.no_grad():
                outputs = model(**inputs)
                # CLSトークンの埋め込みを取得
                embeddings = outputs.last_hidden_state[:, 0, :]
                return embeddings.cpu().numpy().squeeze()
        else:
            # フォールバック: sentence-transformers
            return model.encode(text, convert_to_numpy=True)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """複数テキストの埋め込み生成（ONNX対応）"""
        model = self._load_model()
        
        if self.tokenizer:
            # ONNXモデル使用
            inputs = self.tokenizer(
                texts, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            with torch.no_grad():
                outputs = model(**inputs)
                # CLSトークンの埋め込みを取得
                embeddings = outputs.last_hidden_state[:, 0, :]
                return embeddings.cpu().numpy()
        else:
            # フォールバック: sentence-transformers
            return model.encode(texts, convert_to_numpy=True)


# グローバルインスタンス
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        # ここではクラスを作るだけで、モデルのロードはまだしない
        _embedding_service = EmbeddingService()
    return _embedding_service