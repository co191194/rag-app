import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import MagicMock


def test_chunk_test_logic():
    text = "a" * 500
    chunck_size = 300
    # main の実装と同じロジックをテストする
    chunks = [text[i : i + chunck_size] for i in range(0, len(text), chunck_size)]

    # 検証
    assert len(chunks) == 2
    assert chunks[0] == "a" * 300
    assert chunks[1] == "a" * 200


########################################################################################
# アップロードエンドポイントのテスト
########################################################################################


# アップロードエンドポイントが正常に動作し、期待されるレスポンスを返すことをテスト
@pytest.mark.asyncio
async def test_upload_endpoint_success(mocker):

    # PdfReaderもモック化して、PDFの内容を返すようにする
    mock_pdf_reader = mocker.patch("main.PdfReader")
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "a" * 500
    mock_pdf_reader.return_value.pages = [mock_page]

    # OpenAI API クライアントをモック化
    mock_embedding = mocker.patch("main.client.embeddings.create")
    mock_embedding.return_value.data = [MagicMock(embedding=[0.1] * 1536)]

    # DB接続もモック化
    mocker.patch("main.get_db_connection")
    mocker.patch("main.register_vector")

    # FastAPIのテストクライアントを使用してエンドポイントをテスト
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        files = {"file": ("test.pdf", b"dummy content")}
        response = await ac.post("/upload", files=files)

    # 検証
    assert response.status_code == 200
    assert "チャンク数: 2" in response.json()["message"]


# PDF以外のファイルをアップロードした場合、400エラーが返されることをテスト
@pytest.mark.asyncio
async def test_upload_endpoint_file_type_error(mocker):
    # FastAPIのテストクライアントを使用してエンドポイントをテスト
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        files = {"file": ("test.txt", b"dummy content")}
        response = await ac.post("/upload", files=files)

    # 検証
    assert response.status_code == 400
    assert response.json()["detail"] == "PDFファイルのみアップロード可能です。"


########################################################################################
# チャットエンドポイントのテスト
########################################################################################


# チャットエンドポイントが正常に動作し、期待されるレスポンスを返すことをテスト
@pytest.mark.asyncio
async def test_chat_endpoint_success(mocker):
    # OpenAI API クライアントをモック化
    mock_embedding = mocker.patch("main.client.embeddings.create")
    mock_embedding.return_value.data = [MagicMock(embedding=[0.1] * 1536)]

    mock_chat = mocker.patch("main.client.chat.completions.create")
    mock_chat.return_value.choices = [
        MagicMock(message=MagicMock(content="Test response"))
    ]

    # DB接続もモック化
    mocker.patch("main.get_db_connection")
    mocker.patch("main.register_vector")

    # FastAPIのテストクライアントを使用してエンドポイントをテスト
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/chat", json={"query": "Test query"})

    # 検証
    assert response.status_code == 200
    assert response.json()["answer"] == "Test response"


# チャットエンドポイントでOpenAI APIの呼び出しが失敗した場合、500エラーが返されることをテスト
@pytest.mark.asyncio
async def test_chat_endpoint_open_api_error(mocker):
    # OpenAI API クライアントをモック化してエラーを発生させる
    mock_embedding = mocker.patch("main.client.embeddings.create")
    mock_embedding.side_effect = Exception("OpenAI API error")

    # FastAPIのテストクライアントを使用してエンドポイントをテスト
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post("/chat", json={"query": "Test query"})

    # 検証
    assert response.status_code == 500
    assert response.json()["detail"] == "チャットの処理中にエラーが発生しました。"
