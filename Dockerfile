FROM python:3.9-slim
WORKDIR /app

# 必要なパッケージのインストール（netcat-openbsd と cryptography のビルド依存関係）
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    build-essential \
    libffi-dev \
    libssl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x wait-for-it.sh
EXPOSE 5000
CMD ["./wait-for-it.sh", "mysql", "3306", "--", "python", "run.py"]
