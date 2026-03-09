"""
FAISSベクトルストアサービス
ユーザーごとにFAISSインデックスを管理
"""
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# 起動時に一度だけFAISSをインポート
try:
    import faiss
    print("✅ FAISS imported successfully at startup")
    FAISS_AVAILABLE = True
except ImportError as e:
    print(f"❌ FAISS import failed: {e}")
    FAISS_AVAILABLE = False
    faiss = None

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
        self.index = faiss.IndexFlatIP(self.dimension)  # 内積インデックスに変更
        self.metadata = []
        logger.info(f"Created new index for user {self.user_id}")
    
    def add_document(self, document_id: int, title: str, content: str, embedding: List[float]):
        """ドキュメントをFAISSインデックスに追加"""
        import faiss
        import numpy as np
        
        if self.index is None:
            self.index = faiss.IndexFlatIP(self.dimension)  # 内積インデックスに統一
        
        # 埋め込みベクトルをnumpy配列に変換
        embedding_array = np.array([embedding]).astype('float32')
        
        # L2正規化を適用
        embedding_array = faiss.normalize_L2(embedding_array)
        
        # インデックスにベクトルを追加
        self.index.add(embedding_array)
        
        # メタデータを追加
        self.metadata.append({
            'document_id': document_id,
            'title': title,
            'content': content
        })
        
        # 即時保存
        self._save()
        logger.info(f"Added document {document_id} to index. Total: {len(self.metadata)}")
    
    def remove_document(self, document_id: int):
        """ドキュメントをFAISSから削除"""
        if not FAISS_AVAILABLE:
            return
        
        # 削除対象のメタデータを探す
        new_metadata = []
        remove_indices = []
        
        for i, meta in enumerate(self.metadata):
            if meta['document_id'] != document_id:
                new_metadata.append(meta)
            else:
                remove_indices.append(i)
        
        if not remove_indices:
            return  # 削除対象がなかった
        
        # 新しいインデックスを作成
        if new_metadata:
            # 残りのドキュメントで新しいインデックスを作成
            new_index = faiss.IndexFlatIP(self.dimension)  # IndexFlatIPに統一
            
            # 既存の埋め込みを再構築（簡易的な実装）
            # 実際には埋め込みを保存しておく必要がある
            for i in range(self.index.ntotal):
                if i not in remove_indices:
                    embedding = self.index.reconstruct(i)
                    # L2正規化を適用して追加
                    normalized_embedding = faiss.normalize_L2(embedding.reshape(1, -1))
                    new_index.add(normalized_embedding)
            
            self.index = new_index
            self.metadata = new_metadata
        else:
            # 全部削除の場合
            self.index = faiss.IndexFlatIP(self.dimension)  # IndexFlatIPに統一
            self.metadata = []
        
        self._save()
        logger.info(f"Removed document {document_id} from FAISS")
    
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

# シングルトン管理
_vector_stores = {}

def get_vector_store(user_id: int) -> VectorStore:
    """ユーザーごとのVectorStoreシングルトンを取得"""
    from app.services.embeddings import get_embedding_service
    
    if user_id not in _vector_stores:
        embedding_service = get_embedding_service()
        _vector_stores[user_id] = VectorStore(user_id, dimension=embedding_service.dimension)
        logger.info(f"Created new VectorStore for user {user_id}")
    
    return _vector_stores[user_id]