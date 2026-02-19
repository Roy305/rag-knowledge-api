"""
FAISSベクトルストアサービス
ユーザーごとにFAISSインデックスを管理
"""
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# import faiss  <-- ここからは消す！

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, user_id: int, dimension: int = 384, storage_dir: str = "./vector_stores"):
        self.user_id = user_id
        self.dimension = dimension
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        self.index_path = self.storage_dir / f"user_{user_id}_index.faiss"
        self.metadata_path = self.storage_dir / f"user_{user_id}_metadata.pkl"
        
        self.index = None
        self.metadata = []
        
        # 既存インデックスの読み込み
        self._load_or_create()
    
    def _load_or_create(self):
        """既存インデックスを読み込むか、新規作成"""
        import faiss  # ここでインポート！
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
                with open(self.metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded existing index for user {self.user_id}: {len(self.metadata)} documents")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """新規インデックス作成"""
        import faiss  # ここでインポート！
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info(f"Created new index for user {self.user_id}")
    
    def add_document(self, document_id: int, title: str, content: str, embedding: np.ndarray):
        self.index.add(embedding.reshape(1, -1))
        self.metadata.append({
            'document_id': document_id,
            'title': title,
            'content': content
        })
        self._save()
        logger.info(f"Added document {document_id} for user {self.user_id}")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[dict, float]]:
        if self.index.ntotal == 0:
            return []
        distances, indices = self.index.search(query_embedding.reshape(1, -1), min(top_k, self.index.ntotal))
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(distance)))
        return results
    
    def _save(self):
        import faiss  # ここでインポート！
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def get_document_count(self) -> int:
        return len(self.metadata)

def get_vector_store(user_id: int) -> VectorStore:
    from app.services.embeddings import get_embedding_service
    embedding_service = get_embedding_service()
    return VectorStore(user_id, dimension=embedding_service.dimension)