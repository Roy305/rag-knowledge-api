# RAG Knowledge API

🤖 **RAG-powered Knowledge Base API with FAISS Vector Search**

高品質なRAG（Retrieval-Augmented Generation）チャットシステム。FAISSベクトル検索とGroq LLMを組み合わせ、ドキュメントに基づいた正確な回答を提供します。

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![ONNX](https://img.shields.io/badge/ONNX-Optimized-orange.svg)](https://onnx.ai/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 特徴

- 🧠 **インテリジェント検索**: FAISSベクトル検索で高速な類似度検索
- 📄 **マルチフォーマット対応**: PDF, TXT, CSV, DOC, DOCX
- 🚀 **ONNX最適化**: INT8量子化で最大限のパフォーマンス
- 🎨 **プレミアムUI**: 高品質なチャットインターフェース
- 🔐 **認証システム**: JWTベースのセキュア認証
- 📱 **レスポンシブ**: モバイル対応デザイン
- ⚡ **高速**: Render無料枠で最適化

## 🛠️ 技術スタック

### バックエンド
- **FastAPI**: 高性能Webフレームワーク
- **FAISS**: ベクトル検索ライブラリ
- **ONNX**: モデル最適化
- **PostgreSQL**: データベース
- **Groq**: LLM API (llama-3.1-8b-instant)
- **Alembic**: データベースマイグレーション

### フロントエンド
- **Next.js**: Reactフレームワーク
- **TypeScript**: 型安全
- **Tailwind CSS**: モダンCSS
- **shadcn/ui**: UIコンポーネント

### インフラ
- **Render**: ホスティングプラットフォーム
- **Vercel**: フロントエンドデプロイ

## 🚀 クイックスタート

### 環境要件
- Python 3.12+
- Node.js 18+
- PostgreSQL
- Docker Desktop (推奨)

### 方法1: Dockerで起動（推奨）

```bash
# 1. リポジトリクローン
git clone https://github.com/Roy305/rag-knowledge-api.git
cd rag-knowledge-api

# 2. Dockerで起動（全ての依存関係を含む）
docker compose up

# 3. ブラウザで確認
# API: http://localhost:8000/docs
# DB: localhost:5432
```

### 方法2: ローカル開発

```bash
# 1. リポジトリクローン
git clone https://github.com/Roy305/rag-knowledge-api.git
cd rag-knowledge-api

# 2. 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存関係インストール
pip install poetry
poetry install

# 4. 環境変数設定
cp .env.example .env
# .envファイルを編集して必要な変数を設定

# 5. データベースマイグレーション
alembic upgrade head

# 6. ONNXモデル変換（初回のみ）
python convert_model.py

# 7. サーバー起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 🐳 Docker vs ローカル開発

| 項目 | Docker | ローカル | 推奨 |
|------|--------|----------|--------|
| セットアップ容易さ | 😊 一発 | ⚠️ 手動 | Docker |
| 環境再現性 | 😊 高い | 😡 低い | Docker |
| メモリ使用量 | ⚠️ 高い | 😊 低い | ローカル |
| 開発速度 | ⚠️ 遅い | 😊 速い | ローカル |
| ビルド時間 | ⚠️ 長い | 😊 速い | ローカル |
| デバッグ容易さ | ⚠️ 複雑 | 😊 簡単 | ローカル |

**結論:**
- **初心者**: Docker推奨（環境構築が簡単）
- **経験者**: ローカル開発推奨（開発速度が速い）

### フロントエンドセットアップ

```bash
# 1. フロントエンドディレクトリに移動
cd ../rag-knowledge-frontend

# 2. 依存関係インストール
npm install

# 3. 環境変数設定
cp .env.example .env.local
# .env.localファイルを編集

# 4. 開発サーバー起動
npm run dev
```

## 🔧 環境変数

### バックエンド (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/rag_db
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=development
```

### フロントエンド (.env.local)
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## 📖 APIドキュメント

### 認証エンドポイント
- `POST /auth/register` - ユーザー登録
- `POST /auth/login` - ログイン
- `GET /auth/me` - ユーザー情報取得

### ドキュメント管理
- `POST /documents/upload` - ドキュメントアップロード
- `GET /documents` - ドキュメント一覧
- `DELETE /documents/{id}` - ドキュメント削除
- `GET /documents/{id}` - ドキュメント詳細

### 検索
- `POST /search` - RAG検索

### APIドキュメント
サーバー起動後、以下のURLでSwagger UIを確認できます：
- http://localhost:8000/docs

## 🚀 Renderデプロイ

### 1. バックエンドデプロイ
```bash
# GitHubにプッシュ
git push origin main

# Renderダッシュボードで：
# 1. 新しいWeb Service作成
# 2. GitHubリポジトリ連携
# 3. Python 3 Runtime選択
# 4. 環境変数設定
# 5. デプロイ実行
```

### 2. フロントエンドデプロイ
```bash
# Vercelにデプロイ
npm run build
vercel --prod
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
│   └── main.py        # FastAPIアプリケーション
├── alembic/           # データベースマイグレーション
├── tests/             # テスト
├── convert_model.py   # ONNX変換スクリプト
└── pyproject.toml     # 依存関係

rag-knowledge-frontend/
├── src/
│   ├── app/           # Next.jsページ
│   ├── components/    # Reactコンポーネント
│   └── config/        # 設定ファイル
└── package.json       # 依存関係
```

## 🧪 テスト

```bash
# バックエンドテスト
pytest

# フロントエンドテスト
npm test
```

## 🎯 使い方

1. **ユーザー登録**: `/signup` でアカウント作成
2. **ログイン**: 認証トークン取得
3. **ドキュメントアップロード**: PDFやテキストファイルをアップロード
4. **チャット**: アップロードしたドキュメントについて質問
5. **回答**: AIがドキュメントに基づいて回答

## 🔍 機能詳細

### RAG検索
- FAISSベクトル検索で関連ドキュメントを特定
- Groq LLMで自然な回答を生成
- 参照資料の明示

### ファイル処理
- PDFテキスト抽出
- UTF-8エンコーディング対応
- 1MBサイズ制限

### パフォーマンス最適化
- ONNX + INT8量子化
- FAISSインデックス最適化
- メモリ使用量最小化

## 🤝 貢献

1. Forkする
2. 機能ブランチ作成 (`git checkout -b feature/AmazingFeature`)
3. コミット (`git commit -m 'Add some AmazingFeature'`)
4. プッシュ (`git push origin feature/AmazingFeature`)
5. Pull Request作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 🙏 謝辞

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能Webフレームワーク
- [FAISS](https://faiss.ai/) - ベクトル検索ライブラリ
- [Groq](https://groq.com/) - 高速LLM API
- [Next.js](https://nextjs.org/) - Reactフレームワーク
- [Tailwind CSS](https://tailwindcss.com/) - CSSフレームワーク

## 📞 サポート

問題がある場合や質問がある場合は、[Issues](https://github.com/Roy305/rag-knowledge-api/issues) を作成してください。

---

**🚀 高品質なRAGシステムを構築しましょう！**

