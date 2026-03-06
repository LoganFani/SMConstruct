import os
import sys
import platform
import subprocess
import zipfile
from pathlib import Path

# -- Bootstrap: resolve project root before importing utils --------------------
ROOT = Path(__file__).resolve().parent
BIN_DIR = ROOT / "backend" / "bin"
MODELS_DIR = ROOT / "llama" / "models"
MISTRALQ4_PATH =  MODELS_DIR / "mistral-7b-instruct-v0.2.Q4_0.gguf"
sys.path.insert(0, str(ROOT))


# Guard to ensure this only runs on Windows
if platform.system() != "Windows":
    print("Error: This setup script is configured for Windows only.")
    print("Please use Docker Compose for other platforms.")
    sys.exit(1)

def run(cmd, **kwargs):
    print(">>", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True, **kwargs)

def which(cmd) -> bool:
    import shutil
    return shutil.which(cmd) is not None

# -- Python dependencies -------------------------------------------------------

def setup_venv():
    venv_dir = ROOT / "env"
    if venv_dir.exists():
        print("✓ Virtual environment already exists")
    else:
        print("⬇  Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(venv_dir)])
        print("✓ Virtual environment created")

    pip = venv_dir / "Scripts" / "pip.exe"

    print("⬇  Installing Python dependencies...")
    run([str(pip), "install", "-r", str(ROOT / "requirements.txt"), "-q"])
    print("✓ Python dependencies installed")

# -- Node / frontend -----------------------------------------------------------

def setup_frontend():
    frontend_dir = ROOT / "frontend"
    if not frontend_dir.exists():
        print("⚠  No frontend directory found, skipping.")
        return

    if not which("node"):
        print("✗ Node.js not found. Please install it from https://nodejs.org")
        sys.exit(1)

    print("⬇  Installing frontend dependencies...")
    subprocess.run(["npm", "install"], cwd=str(frontend_dir), shell=True, check=True)
    print("✓ Frontend dependencies installed")

# -- ffmpeg --------------------------------------------------------------------

def install_ffmpeg():
    if which("ffmpeg"):
        print("✓ ffmpeg already on PATH")
        return

    local_ffmpeg = BIN_DIR / "ffmpeg.exe"
    if local_ffmpeg.exists():
        print("✓ ffmpeg already in bin dir")
        return

    print("⬇  Downloading ffmpeg for Windows...")
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = BIN_DIR / "ffmpeg.zip"
    
    BIN_DIR.mkdir(exist_ok=True)
    run(["curl", "-L", url, "-o", str(zip_path)])
    
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(BIN_DIR)
    
    zip_path.unlink()
    
    # Move files out of the extracted subfolder to /bin
    ffmpeg_bin_dir = next(BIN_DIR.glob("ffmpeg-*/bin"))
    for f in ffmpeg_bin_dir.iterdir():
        f.rename(BIN_DIR / f.name)
    
    print(f"✓ ffmpeg extracted to {BIN_DIR}")

# -- yt-dlp --------------------------------------------------------------------

def install_ytdlp():
    if which("yt-dlp"):
        print("✓ yt-dlp already on PATH")
        return

    local_ytdlp = BIN_DIR / "yt-dlp.exe"
    if local_ytdlp.exists():
        print("✓ yt-dlp already in bin dir")
        return

    print("⬇  Downloading yt-dlp.exe...")
    url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    run(["curl", "-L", url, "-o", str(local_ytdlp)])
    print(f"✓ yt-dlp downloaded to {local_ytdlp}")

# -- LLM model -----------------------------------------------------------------

def install_model():
    if MISTRALQ4_PATH.exists():
        print("✓ Model already exists")
        return

    print("⬇  Downloading Mistral model (~4GB)...")
    url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_0.gguf"
    run(["curl", "-L", "--progress-bar", url, "-o", str(MISTRALQ4_PATH)])
    print("✓ Model downloaded to:", MISTRALQ4_PATH)

# -- .env ----------------------------------------------------------------------

def setup_env_file():
    env_path = ROOT / ".env"
    if env_path.exists():
        print("✓ .env already exists")
        return
    print(" Creating .env...")
    env_path.write_text("PROJECT_ROOT=.\nANKI_CONNECT_URL=http://127.0.0.1:8765\n")
    print("✓ .env created")

# -- Launcher scripts ----------------------------------------------------------

def create_launchers():
    start = ROOT / "start.bat"
    start.write_text(
        "@echo off\n"
        "echo Starting Lang Reader...\n"
        "cd /d %~dp0\n"
        "start \"Lang Reader Backend\" cmd /k \"env\\Scripts\\activate && python -m uvicorn backend.main:app --reload\"\n"
        "timeout /t 3 >nul\n"
        "start \"Lang Reader Frontend\" cmd /k \"cd frontend && npm run dev\"\n"
        "timeout /t 3 >nul\n"
        "start http://localhost:5173\n"
    )
    
    stop = ROOT / "stop.bat"
    stop.write_text(
        "@echo off\n"
        "echo Stopping Lang Reader...\n"
        "taskkill /FI \"WINDOWTITLE eq Lang Reader Backend\" /T /F >nul 2>&1\n"
        "taskkill /FI \"WINDOWTITLE eq Lang Reader Frontend\" /T /F >nul 2>&1\n"
        "echo Done.\n"
    )
    print("✓ Created Windows .bat launchers")

# -- Main ----------------------------------------------------------------------

def main():
    print("\n╔══════════════════════════════════╗")
    print("║      SMConstruct Windows Setup v0.1 ║")
    print("╚══════════════════════════════════╝\n")

    setup_env_file()
    setup_venv()
    setup_frontend()
    install_ffmpeg()
    install_ytdlp()
    install_model()
    create_launchers()

    print("\n✓ Setup Complete! Run ./start.bat to launch.")

if __name__ == "__main__":
    main()