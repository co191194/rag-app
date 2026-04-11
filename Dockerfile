FROM python:3.13-slim

WORKDIR /app

# キャッシュを効かせてパッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードのコピーはdocker-composeで行う