# AI Document Assistant (RAG System)

社内の就業規則やマニュアルなどのPDFドキュメントをアップロードし、その内容に基づいてAIが回答を生成するRAG（Retrieval-Augmented Generation：検索拡張生成）システムです。

## 🚀 概要
本プロジェクトは、LLM（大規模言語モデル）の弱点である「最新情報の欠如」や「ハルシネーション（嘘）」を克服するため、自社データを検索基盤として活用する実務的なAIアプリケーションです。
フロントエンド、バックエンド、データベース、インフラをすべてコンテナ化し、モダンな技術スタックで構築されています。

## 🛠 技術スタック

### Frontend
- **Vue 3 (TypeScript)** - Composition API / Vite
- **Tailwind CSS** - スタイリング
- **shadcn-vue** - UIコンポーネントライブラリ
- **pnpm** - 高速なパッケージ管理
- **Axios** - API通信

### Backend
- **Python 3.13** - 最新の言語仕様を活用
- **FastAPI** - 高速な非同期Webフレームワーク
- **OpenAI API**
    - `text-embedding-3-small`: ドキュメントのベクトル化（埋め込み）
    - `gpt-4o-mini`: 検索結果に基づいた回答生成
- **psycopg3 / pgvector** - ベクトルデータの操作と保存

### Database
- **PostgreSQL 16 (pgvector)** - ベクトル検索対応のRDBMS

### Infrastructure / DevTools
- **Docker / Docker Compose** - 開発環境の完全コンテナ化
- **VSCode (Dev Containers)** - 開発環境の標準化

## 💡 主な機能
1. **ドキュメント・インジェクション**
   - PDFファイルをアップロードし、テキストを自動抽出。
   - テキストを適切なサイズにチャンキングし、ベクトル化してデータベースに保存。
2. **AIチャット（RAG）**
   - ユーザーの質問に対し、データベースから関連性の高い文脈（Context）を検索。
   - 検索された情報のみに基づいてAIが回答を構成。
3. **モダンなUI/UX**
   - shadcn-vueによるクリーンなデザイン。
   - ファイルアップロードからチャットまでの一貫したユーザー体験。

## 🏗 アーキテクチャ
1. **Upload**: User -> Vue3 -> FastAPI -> PDF Extraction -> Embedding (OpenAI) -> PostgreSQL (pgvector)
2. **Chat**: User -> Vue3 -> FastAPI -> Embedding (Query) -> Vector Search (PostgreSQL) -> Prompt Construction -> LLM (OpenAI) -> Response

## 📂 プロジェクト構成
```text
.
├── docker-compose.yml
├── backend/
│   ├── main.py            # APIサーバー・RAGロジック
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env               # APIキー設定
└── frontend/
    ├── src/
    │   ├── App.vue        # メインUI実装
    │   └── components/    # shadcn-vueコンポーネント
    ├── Dockerfile
    └── pnpm-lock.yaml
```

## ⚡️ 起動方法
Dockerがインストールされている環境であれば、以下のコマンドで全環境が立ち上がります。

```bash
docker compose up -d --build
```

起動後、以下のURLにアクセスしてください。
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
