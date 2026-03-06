FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    cmake \
    curl \
    ffmpeg \
    sed \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY backend/ /app/backend/
COPY utils/ /app/utils/
COPY llama/grammar/ /app/llama/grammar/
COPY download_model.sh /app/download_model.sh


ENV PYTHONPATH=/app

#Fix permissions and Line Endings
RUN sed -i 's/\r$//' /app/download_model.sh && \
    chmod +x /app/download_model.sh

EXPOSE 8000

CMD ["./download_model.sh"]