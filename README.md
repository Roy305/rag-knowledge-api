# RAG Knowledge API

🔍 **ドキュメント検索＆質問応答API**

アップロードしたドキュメントに基づいて、質問に正確に回答するRAGシステム。FAISSベクトル検索とJina AI埋め込み、Groq LLMを組み合わせて使用します。

## 📋 プロジェクト概要

### できること
- 📄 **ドキュメントアップロード**: PDF、テキストファイルを登録
- 🔍 **インテリジェント検索**: ベクトル検索で関連情報を特定
- 💬 **質問応答**: ドキュメント内容に基づいて回答生成
- 👤 **ユーザー管理**: JWT認証でセキュアなアクセス
- 📱 **マルチデバイス**: レスポンシブ対応

### アーキテクチャ
```
ユーザー → API → 認証 → ドキュメントアップロード
                ↓
          テキスト → Jina埋め込み → FAISSベクトル化
                ↓
          質問 → 埋め込み → 類似度検索 → Groq LLM → 回答
```

## 🛠️ 技術スタック

### バックエンド
- **FastAPI**: 高性能Webフレームワーク
- **Jina AI**: 埋め込み生成 (jina-embeddings-v3)
- **FAISS**: ベクトル検索エンジン
- **Groq**: LLM API (llama-3.1-8b-instant)
- **PostgreSQL**: ユーザーデータ保存
- **Alembic**: データベースマイグレーション

### インフラ
- **Render**: APIホスティング
- **Docker**: コンテナ化デプロイ

## 🚀 セットアップ手順

### 1. 環境準備
```bash
# リポジトリクローン
git clone https://github.com/Roy305/rag-knowledge-api.git
cd rag-knowledge-api

# 環境変数設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

### 2. Dockerで起動（推奨）
```bash
# 全ての依存関係を含めて起動
docker compose up

# 確認
# API: http://localhost:8000/docs
# DB: localhost:5432
```

### 3. ローカル開発
```bash
# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install poetry
poetry install

# サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 環境変数設定

### .envファイル
```env
# データベース
DATABASE_URL=postgresql://user:password@localhost:5432/rag_db

# 認証
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AIサービス
GROQ_API_KEY=gsk_xxxx  # https://console.groq.com/keys
JINA_API_KEY=jina_xxxx  # https://jina.ai/embeddings/

# 環境
ENVIRONMENT=development
```

## 📖 使い方

### 1. アカウント作成
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 2. ログイン
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 3. ドキュメントアップロード
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

### 4. 質問検索
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "プロジェクトの概要は？", "top_k": 3}'
```

## 📁 プロジェクト構造
```
rag-knowledge-api/
├── app/
│   ├── api/           # APIエンドポイント
│   ├── core/          # 認証・依存関係
│   ├── models/        # データベースモデル
│   ├── schemas/       # Pydanticスキーマ
│   ├── services/      # ビジネスロジック
│   └── main.py        # FastAPIアプリ
├── alembic/           # データベースマイグレーション
├── tests/             # テスト
├── pyproject.toml     # 依存関係
└── README.md          # プロジェクト説明
```

## 🚀 デプロイ

### Renderへのデプロイ
1. GitHubにプッシュ
2. RenderでWeb Service作成
3. リポジトリ連携
4. 環境変数設定
5. デプロイ実行

### 環境変数（Render）
- `DATABASE_URL`: PostgreSQL接続文字列
- `SECRET_KEY`: JWT秘密鍵
- `GROQ_API_KEY`: Groq APIキー
- `JINA_API_KEY`: Jina AI APIキー

## 📊 API仕様

### 認証エンドポイント
- `POST /auth/register` - ユーザー登録
- `POST /auth/login` - ログイン
- `GET /auth/me` - ユーザー情報

### ドキュメント管理
- `POST /documents/upload` - ファイルアップロード
- `GET /documents` - ドキュメント一覧
- `GET /documents/{id}` - ドキュメント詳細
- `DELETE /documents/{id}` - ドキュメント削除

### 検索
- `POST /search` - RAG検索

### APIドキュメント
起動後: http://localhost:8000/docs

## 🧪 テスト
```bash
# バックエンドテスト
pytest

# カバレッジ確認
pytest --cov=app
```

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 📞 サポート

問題報告: [GitHub Issues](https://github.com/Roy305/rag-knowledge-api/issues)

---

**🔍 ドキュメントベースの知的検索システムを構築！**
