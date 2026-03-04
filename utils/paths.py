import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(os.getenv("PROJECT_ROOT", ".")).resolve()

VIDEO_STORAGE  = ROOT / "backend" / "storage" / "videos"
SUBS_STORAGE   = ROOT / "backend" / "storage" / "subs"
FRAMES_STORAGE = ROOT / "backend" / "storage" / "frames"
AUDIO_STORAGE  = ROOT / "backend" / "storage" / "audio"
BIN_DIR        = ROOT / "backend" / "bin"

DATA_BASE_PATH = ROOT / "backend" / "db" / "data.db"

MODELS_DIR = ROOT / "llama" / "models"
MISTRALQ4_PATH = MODELS_DIR / "mistral-7b-instruct-v0.2.Q4_0.gguf"
LLAMA_GRAMMAR_DIR = ROOT / "llama" / "grammar"
LLAMA_GRAMMAR_JSON_PATH = LLAMA_GRAMMAR_DIR / "json.gbnf"

ANKI_CONNECT_URL = os.getenv("ANKI_CONNECT_URL", "http://127.0.0.1:8765")


# Ensure directories exist (note: parent dir for the DB file, not the file itself)
VIDEO_STORAGE.mkdir(parents=True, exist_ok=True)
SUBS_STORAGE.mkdir(parents=True, exist_ok=True)
FRAMES_STORAGE.mkdir(parents=True, exist_ok=True)
AUDIO_STORAGE.mkdir(parents=True, exist_ok=True)
BIN_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_BASE_PATH.parent.mkdir(parents=True, exist_ok=True)