
import subprocess
MODEL_DIR="/app/llama/models"
MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_0.gguf"

def main():

    cmd = ["curl", "-L", MODEL_URL, "-o", MODEL_DIR]

    subprocess.run(cmd)

    subprocess.run(["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"])


if __name__ == "__main__":
    main()
