import os
import psycopg
from pgvector.psycopg import register_vector
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# DB接続情報
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_db_connection():
    """PostgreSQLデータベースへの接続を確立する関数"""
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            autocommit=True,
        )
        return conn
    except Exception as e:
        print(f"データベースへの接続中にエラーが発生しました: {e}")
        return None


def setup_database():
    """データベースとテーブルをセットアップする関数"""
    with get_db_connection() as conn:
        if conn is None:
            print("データベース接続に失敗しました。セットアップを中止します。")
            return
        # pgvector拡張機能を有効にする (存在しない場合は作成)
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # pgvectorにvector型を認識させる
        register_vector(conn)

        # テーブルを作成 (存在する場合は削除して作り直す)
        conn.execute("DROP TABLE IF EXISTS documents;")
        conn.execute("""
            CREATE TABLE documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                -- 1536次元のベクトルを格納するためのカラム (text-embedding-3-smallの出力サイズに合わせる)
                embedding VECTOR(1536) NOT NULL
            );
        """)
        print("データベースのセットアップが完了しました。")


def insert_and_search_test():
    """テストデータの挿入と検索を行う関数"""
    # テスト用の文章
    texts = [
        "出張時の日当は、国内であれば一律3000円支給されます。",
        "リモートワークは週に最大3日まで許可されています。",
        "交通費の精算は月末までに経理システムから申請してください。",
    ]

    print("\n テストデータの挿入と検索を開始します...")
    with get_db_connection() as conn:
        if conn is None:
            print("データベース接続に失敗しました。テストを中止します。")
            return

        register_vector(conn)
        for text in texts:
            # ベクトル化
            response = client.embeddings.create(
                input=text, model="text-embedding-3-small"
            )
            embedding = response.data[0].embedding

            # データベースに挿入
            conn.execute(
                "INSERT INTO documents (content, embedding) VALUES (%s, %s);",
                (text, embedding),
            )

        print("保存完了!")

    # 検索のテスト
    query = "在宅勤務のルールについて教えて"
    print(f"\n検索クエリ: {query}")

    # 質問文をベクトル化
    query_response = client.embeddings.create(
        input=query, model="text-embedding-3-small"
    )
    query_embedding = query_response.data[0].embedding

    # ベクトル類似度検索 (コサイン類似度を使用)
    with get_db_connection() as conn:
        if conn is None:
            print("データベース接続に失敗しました。検索を中止します。")
            return

        register_vector(conn)
        # <=> 演算子はpgvectorが提供するベクトル距離演算子で、1 - (embedding <=> query_embedding) で類似度を計算
        results = conn.execute(
            """
            SELECT content, 1 - (embedding <=> %s::vector) AS similarity
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT 2;
        """,
            (query_embedding, query_embedding),
        ).fetchall()

        print("\n検索結果 (意味が近い順) :")
        for content, similarity in results:
            print(f"類似度: {similarity:.3f} | 内容: {content}")


if __name__ == "__main__":
    setup_database()
    insert_and_search_test()
