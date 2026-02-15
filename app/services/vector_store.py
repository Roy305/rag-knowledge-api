"""
FAISSベクトルストアサービス

ユーザーごとにFAISSインデックスを管理
"""
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISSベクトルストア
    
    ユーザーごとにインデックスとメタデータを管理
    """
    
    def __init__(self, user_id: int, dimension: int = 384, storage_dir: str = "./vector_stores"):
        """
        初期化
        
        Args:
            user_id: ユーザーID
            dimension: ベクトルの次元数（モデルに依存）
            storage_dir: インデックス保存ディレクトリ
        """
        self.user_id = user_id
        self.dimension = dimension
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # ファイルパス
        self.index_path = self.storage_dir / f"user_{user_id}_index.faiss"
        self.metadata_path = self.storage_dir / f"user_{user_id}_metadata.pkl"
        
        # インデックスとメタデータ
        self.index = None
        self.metadata = []  # [(document_id, title, content), ...]
        
        # 既存インデックスの読み込み
        self._load_or_create()
    
    def _load_or_create(self):
        """既存インデックスを読み込むか、新規作成"""
        if self.index_path.exists() and self.metadata_path.exists():
            try:
                # 既存インデックス読み込み
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
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info(f"Created new index for user {self.user_id}")
    
    def add_document(self, document_id: int, title: str, content: str, embedding: np.ndarray):
        """
        ドキュメントを追加
        
        Args:
            document_id: ドキュメントID
            title: タイトル
            content: 本文
            embedding: 埋め込みベクトル
        """
        # ベクトルを追加
        self.index.add(embedding.reshape(1, -1))
        
        # メタデータを追加
        self.metadata.append({
            'document_id': document_id,
            'title': title,
            'content': content
        })
        
        # 保存
        self._save()
        
        logger.info(f"Added document {document_id} for user {self.user_id}")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[dict, float]]:
        """
        類似検索
        
        Args:
            query_embedding: クエリの埋め込みベクトル
            top_k: 返す結果の数
            
        Returns:
            [(metadata, distance), ...] のリスト
        """
        if self.index.ntotal == 0:
            return []
        
        # 検索実行
        distances, indices = self.index.search(query_embedding.reshape(1, -1), min(top_k, self.index.ntotal))
        
        # 結果を整形
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                results.append((self.metadata[idx], float(distance)))
        
        return results
    
    def remove_document(self, document_id: int):
        """
        ドキュメントを削除
        
        注意: FAISSは削除機能がないので、インデックスを再構築する
        """
        # メタデータから削除
        self.metadata = [m for m in self.metadata if m['document_id'] != document_id]
        
        # インデックスを再構築
        if len(self.metadata) > 0:
            # 全ドキュメントの埋め込みを再取得して再構築
            # （簡易実装: 削除が頻繁でなければこれでOK）
            logger.warning(f"Document {document_id} removed. Index rebuild required.")
            # 実際の再構築はapp/api/documents.pyで行う
        else:
            # 全部削除された場合は新規作成
            self._create_new_index()
        
        self._save()
    
    def _save(self):
        """インデックスとメタデータを保存"""
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def get_document_count(self) -> int:
        """インデックス内のドキュメント数を取得"""
        return len(self.metadata)


def get_vector_store(user_id: int) -> VectorStore:
    """
    ユーザーのベクトルストアを取得
    
    Args:
        user_id: ユーザーID
        
    Returns:
        VectorStore インスタンス
    """
    from app.services.embeddings import get_embedding_service
    embedding_service = get_embedding_service()
    return VectorStore(user_id, dimension=embedding_service.dimension)