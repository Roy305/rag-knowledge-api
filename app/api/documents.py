"""
ドキュメント管理エンドポイント
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentListItem
from app.services.embeddings import get_embedding_service  # ← 追加
from app.services.vector_store import get_vector_store      # ← 追加

router = APIRouter(prefix="/documents", tags=["ドキュメント管理"])


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ドキュメント作成
    
    - 認証必須
    - ユーザーごとに最大10件まで
    - 1ドキュメント最大1MB
    """
    # ドキュメント数制限チェック（10件まで）
    doc_count = db.query(Document).filter(Document.user_id == current_user.id).count()
    if doc_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ドキュメント数の上限（10件）に達しています"
        )
    
    # ドキュメント作成
    new_document = Document(
        user_id=current_user.id,
        title=document_data.title,
        content=document_data.content
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    # ★ 埋め込み生成してFAISSに追加 ★
    try:
        embedding_service = get_embedding_service()
        vector_store = get_vector_store(current_user.id)
        
        # 埋め込み生成
        embedding = embedding_service.embed_text(document_data.content)
        
        # FAISSに追加
        vector_store.add_document(
            document_id=new_document.id,
            title=new_document.title,
            content=new_document.content,
            embedding=embedding
        )
    except Exception as e:
        # 埋め込み追加に失敗してもドキュメント作成は成功させる
        # （後で再試行できるように）
        import logging
        logging.error(f"Failed to add embedding: {e}")
    
    return new_document

    
    return new_document



@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ファイルアップロード
    
    - テキストファイルのみ対応
    - 最大1MB
    """
    # ファイルサイズチェック
    content = await file.read()
    if len(content) > 1_000_000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルサイズは1MB以下にしてください"
        )
    
    # テキストデコード
    try:
        text_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="UTF-8テキストファイルのみ対応しています"
        )
    
    # ドキュメント数制限チェック
    doc_count = db.query(Document).filter(Document.user_id == current_user.id).count()
    if doc_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ドキュメント数の上限（10件）に達しています"
        )
    
    # ドキュメント作成
    new_document = Document(
        user_id=current_user.id,
        title=file.filename,
        content=text_content
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    # ★ 埋め込み生成してFAISSに追加 ★
    try:
        embedding_service = get_embedding_service()
        vector_store = get_vector_store(current_user.id)
        
        # 埋め込み生成
        embedding = embedding_service.embed_text(text_content)
        
        # FAISSに追加
        vector_store.add_document(
            document_id=new_document.id,
            title=new_document.title,
            content=new_document.content,
            embedding=embedding
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to add embedding: {e}")
    
    
    return new_document


@router.get("", response_model=List[DocumentListItem])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ドキュメント一覧取得
    
    - 認証必須
    - 自分のドキュメントのみ表示
    - contentは含めない（一覧表示用）
    """
    documents = db.query(Document)\
        .filter(Document.user_id == current_user.id)\
        .order_by(Document.created_at.desc())\
        .all()
    
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ドキュメント詳細取得
    
    - 認証必須
    - 自分のドキュメントのみ取得可能
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ドキュメントが見つかりません"
        )
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ドキュメント削除
    
    - 認証必須
    - 自分のドキュメントのみ削除可能
    - FAISSインデックスからも削除
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ドキュメントが見つかりません"
        )
    
    # 1. まずDBから削除（これが真実の源泉）
    db.delete(document)
    db.commit()
    
    # 2. その後FAISSから削除
    # 失敗してもDBはすでに削除されてるので、検索結果には表示されない
    try:
        vector_store = get_vector_store(current_user.id)
        vector_store.remove_document(document_id)
    except Exception as e:
        import logging
        logging.error(f"Failed to remove document {document_id} from vector store: {e}")
        # エラーログを残すが、処理は続行
        # FAISSに残っても、次回の検索でDBに存在しないドキュメントは除外される
    
    return None