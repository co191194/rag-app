import os
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

load_dotenv()
client = OpenAI()


def extract_text_from_pdf(pdf_path: str) -> str:
    """PDFファイルからテキストを抽出する関数"""
    try:
        print(f"{pdf_path} からテキストを抽出中...")
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"PDFのテキスト抽出中にエラーが発生しました: {e}")
        return ""


def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """テキストを指定した文字数ごとに分割する関数"""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size]
        chunks.append(chunk)
    return chunks


def get_embedding(text: str) -> list[float]:
    """テキストから埋め込みベクトルを取得する関数"""
    try:
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding
    except Exception as e:
        print(f"埋め込みの取得中にエラーが発生しました: {e}")
        return []


if __name__ == "__main__":
    pdf_path = "sample.pdf"

    if not os.path.exists(pdf_path):
        print(f"PDFファイルが見つかりません: {pdf_path}")
        exit(1)

    # PDFからテキストを抽出
    raw_text = extract_text_from_pdf(pdf_path)
    print(f"抽出完了: 合計 {len(raw_text)} 文字\n")

    if raw_text:
        # テキストをチャンクに分割
        chunks = chunk_text(raw_text)
        print(f"テキストを {len(chunks)} 個のチャンクに分割しました。\n")

        # 最初のチャンクだけ試しにベクトル化してみる
        first_chunk = chunks[0]
        print("<最初のチャンクの内容>")
        print("-" * 40)
        print(first_chunk.strip())
        print("-" * 40)

        print("\nベクトル化中...")
        vector = get_embedding(first_chunk)

        print("\n<ベクトル化の結果>")
        print(
            f"ベクトルの次元数: {len(vector)} 次元"
        )  # 通常は1536次元のベクトルが返されるはず
        print(f"ベクトルの先頭５要素: {vector[:5]}")
        print(
            "\n成功です! テキストがAIに理解できる数値の配列（ベクトル）に変換されました。"
        )

    else:
        print("PDFからテキストを抽出できませんでした。")
