"""
RAG検索エンドポイント
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from openai import OpenAI

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse, SearchSource
from app.services.embeddings import get_embedding_service
from app.services.vector_store import get_vector_store
from app.config import settings

router = APIRouter(prefix="/search", tags=["RAG検索"])


@router.post("", response_model=SearchResponse)
async def search_documents(
    search_request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    RAG検索
    
    処理フロー:
    1. クエリの埋め込み生成
    2. FAISSで類似ドキュメント検索
    3. 関連ドキュメントをコンテキストとしてLLMに渡す
    4. Groq APIで回答生成
    
    - 認証必須
    - 自分のドキュメントのみ検索
    """
    # 埋め込みサービスとベクトルストアを取得
    embedding_service = get_embedding_service()
    vector_store = get_vector_store(current_user.id)
    
    # ドキュメントがない場合
    if vector_store.get_document_count() == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="検索対象のドキュメントがありません。先にドキュメントをアップロードしてください。"
        )
    
    # 1. クエリの埋め込み生成
    query_embedding = embedding_service.embed_text(search_request.query)
    
    # 2. 類似ドキュメント検索
    search_results = vector_store.search(query_embedding, top_k=search_request.top_k)
    
    if not search_results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="関連するドキュメントが見つかりませんでした"
        )
    
    # 3. コンテキスト作成
    context_parts = []
    sources = []
    
    for metadata, distance in search_results:
        # コンテキストに追加
        context_parts.append(f"【{metadata['title']}】\n{metadata['content']}")
        
        # ソース情報を保存
        sources.append(SearchSource(
            document_id=metadata['document_id'],
            title=metadata['title'],
            content=metadata['content'][:200] + "..." if len(metadata['content']) > 200 else metadata['content'],
            distance=distance
        ))
    
    context = "\n\n".join(context_parts)
    
    # 4. Groq APIで回答生成
    try:
        # デバッグ用
        print(f"[DEBUG] GROQ_API_KEY in search.py: {settings.GROQ_API_KEY[:20]}...")
        
        client = OpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": f"""あなたは親切なアシスタントです。
以下のドキュメントに基づいて、ユーザーの質問に正確に答えてください。

【参照ドキュメント】
{context}

【回答のルール】
- ドキュメントの内容に基づいて回答する
- ドキュメントに情報がない場合は「ドキュメントには記載がありません」と答える
- 簡潔で分かりやすく答える
- 日本語で回答する
"""
                },
                {
                    "role": "user",
                    "content": search_request.query
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM API呼び出しエラー: {str(e)}"
        )
    
    return SearchResponse(
        query=search_request.query,
        answer=answer,
        sources=sources
    )