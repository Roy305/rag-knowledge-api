"""
ドキュメント管理エンドポイント
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import PyPDF2
import io

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentListItem
from app.services.embeddings import get_embedding_service
from app.services.vector_store import get_vector_store

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
    
    - テキストファイルとPDF対応
    - 最大1MB
    """
    # メモリ監視開始
    try:
        import psutil
        print(f"📊 メモリ使用量開始: {psutil.virtual_memory().percent}%")
    except ImportError:
        print("⚠️ psutil未インストール - メモリ監視不可")
    
    print("🔍 Step 1: ファイル読み込み開始")
    
    # ファイルサイズチェック
    content = await file.read()
    print(f"📊 ファイルサイズ: {len(content)} bytes")
    
    if len(content) > 1_000_000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイルサイズは1MB以下にしてください"
        )
    
    print("🔍 Step 2: テキスト抽出開始")
    
    # ファイルタイプに応じてテキスト抽出
    if file.content_type == "application/pdf" or file.filename.lower().endswith('.pdf'):
        # PDFからテキスト抽出
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDFの読み取りに失敗しました: {str(e)}"
            )
    else:
        # テキストファイルとして処理
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="UTF-8でデコードできません"
            )
    
    print("🔍 Step 3: 埋め込み生成開始")
    print(f"📊 テキスト長: {len(text_content)} 文字")
    
    # データベースに保存
    new_document = Document(
        user_id=current_user.id,
        title=file.filename,
        content=text_content.strip()
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    print("🔍 Step 4: DB保存完了")

    # ★ 埋め込み生成してFAISSに追加 ★
    try:
        print("📊 埋め込み前メモリ: {psutil.virtual_memory().percent}%")
        
        embedding_service = get_embedding_service()
        vector_store = get_vector_store(current_user.id)
        
        # 埋め込み生成
        print("🔍 Step 5: SentenceTransformerモデルロード開始")
        embedding = embedding_service.embed_text(text_content.strip())
        print("🔍 Step 6: 埋め込み生成完了")
        print(f"📊 埋め込み後メモリ: {psutil.virtual_memory().percent}%")
        
        # FAISSに追加
        vector_store.add_document(
            document_id=new_document.id,
            title=new_document.title,
            content=new_document.content,
            embedding=embedding
        )
        print("🔍 Step 7: FAISS追加完了")
        print(f"📊 最終メモリ: {psutil.virtual_memory().percent}%")
    except Exception as e:
        import logging
        logging.error(f"Failed to add embedding: {e}")
        print(f"❌ 埋め込み処理エラー: {e}")
    
    
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