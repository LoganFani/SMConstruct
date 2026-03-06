#!/bin/bash
MODEL_DIR="/app/llama/models"
MODEL_PATH="$MODEL_DIR/mistral-7b-instruct-v0.2.Q4_0.gguf"
# Replace this URL with the actual Hugging Face/direct link
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_0.gguf"

if [ ! -f "$MODEL_PATH" ]; then
    echo "Model not found. Downloading..."
    mkdir -p "$MODEL_DIR"
    curl -L "$MODEL_URL" -o "$MODEL_PATH"
else
    echo "Model already exists. Skipping download."
fi

# Start the actual backend
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload