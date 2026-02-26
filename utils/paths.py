import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(os.getenv("PROJECT_ROOT", ".")).resolve()

VIDEO_STORAGE = ROOT / "backend" / "storage" / "videos"
SUBS_STORAGE = ROOT / "backend" / "storage" / "subs"
BIN_DIR = ROOT / "backend" / "bin"

MODELS_DIR = ROOT / "llama" / "models"
MISTRALQ4_PATH = MODELS_DIR / "mistral-7b-instruct-v0.2.Q4_0.gguf"

LLAMA_GRAMMAR_DIR = ROOT / "llama" / "grammar"
LLAMA_GRAMMAR_JSON_PATH = LLAMA_GRAMMAR_DIR / "json.gbnf"

# Ensure dirs exist
VIDEO_STORAGE.mkdir(parents=True, exist_ok=True)
SUBS_STORAGE.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
BIN_DIR.mkdir(parents=True, exist_ok=True)