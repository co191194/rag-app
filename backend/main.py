import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import psycopg
from pgvector.psycopg import register_vector
from openai import OpenAI
from pypdf import PdfReader
import io


# FastAPIアプリケーションの初期化
app = FastAPI(title="社内ドキュメントRAG API", version="1.0.0")
# OpenAIクライアントの初期化
client = OpenAI()

# DB接続情報の取得
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "rag_db")
DB_USER = os.getenv("DB_USER", "rag_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rag_password")


def get_db_connection():
    """データベースへのコネクションを取得します。

    Returns:
        Connection: psycopgのコネクションオブジェクト
    """
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=True,
        )
        return conn
    except Exception as e:
        print(f"データベース接続エラー: {e}")
        raise


############################################
# リクエスト/レスポンスモデルの定義
############################################
class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    reference_texts: list[str]


############################################
# APIエンドポイントの定義
############################################
@app.post(
    "/upload",
    summary="PDFドキュメントのアップロード",
    description="PDFドキュメントをアップロードして、RAGシステムに追加します。",
)
async def upload_document(file: UploadFile = File(...)):
    """PDFドキュメントをアップロードして、RAGシステムに追加します。

    Args:
        file (UploadFile): アップロードされたPDFファイル

    Returns:
        dict: アップロード結果
    """
    if file.content_type != "application/pdf" or not file.filename.lower().endswith(
        ".pdf"
    ):
        raise HTTPException(
            status_code=400, detail="PDFファイルのみアップロード可能です。"
        )

    try:
        # PDFの内容を読み取る
        contents = await file.read()
        reader = PdfReader(io.BytesIO(contents))
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        # 簡単なチャンク分割（ 300文字ごと）
        chunks = [
            text[i : i + 300]
            for i in range(0, len(text), 300)
            if text[i : i + 300].strip()
        ]

        # DBに接続して、チャンクをベクトル化して保存
        with get_db_connection() as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                for chunk in chunks:
                    embedding = (
                        client.embeddings.create(
                            input=chunk, model="text-embedding-3-small"
                        )
                        .data[0]
                        .embedding
                    )
                    cur.execute(
                        "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
                        (chunk, embedding),
                    )

        return {
            "message": f"'{file.filename}' のアップロードと処理が完了しました。チャンク数: {len(chunks)}"
        }
    except Exception as e:
        print(f"ドキュメント処理エラー: {e}")
        raise HTTPException(
            status_code=500, detail="ドキュメントの処理中にエラーが発生しました。"
        )


@app.post(
    "/chat",
    response_model=ChatResponse,
    summary="チャットクエリの処理",
    description="ユーザのクエリに対して、RAGシステムから回答と参考テキストを返します。",
)
async def chat_with_documents(request: ChatRequest):
    """ユーザのクエリに対して、RAGシステムから回答と参考テキストを返します。

    Args:
        request (ChatRequest): クエリを含むリクエストボディ

    Returns:
        ChatResponse: 回答と参考テキストを含むレスポンス
    """
    try:
        query = request.query

        # クエリのベクトル化
        query_embedding = (
            client.embeddings.create(input=query, model="text-embedding-3-small")
            .data[0]
            .embedding
        )

        # DBから類似度の高いドキュメントを取得 (トップ2件を取得)
        reference_texts = []
        with get_db_connection() as conn:
            register_vector(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT content
                    FROM documents
                    ORDER BY embedding <=> %s::vector ASC
                    LIMIT 2
                    """,
                    (query_embedding,),
                )
                results = cur.fetchall()

                for row in results:
                    reference_texts.append(row[0])

        # 検索した文章をコンテキストとしてAIに渡して回答を生成
        context_text = "\n\n---\n\n".join(reference_texts)

        system_prompt = f"""
        あなたは会社の優秀なアシスタントです。
        以下の**参考情報**のみに基づいて、ユーザーの質問に答えてください。
        参考情報に答えが含まれていない場合は、「提供された情報ではわかりません」と答えてください。
        
        **参考情報:**
        {context_text}
        """

        chat_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
        )

        answer = chat_response.choices[0].message.content

        return ChatResponse(answer=answer, reference_texts=reference_texts)
    except Exception as e:
        print(f"チャット処理エラー: {e}")
        raise HTTPException(
            status_code=500, detail="チャットの処理中にエラーが発生しました。"
        )
