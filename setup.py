import os
import sys
import platform
import subprocess
import zipfile
import tarfile
from pathlib import Path

# ── Bootstrap: resolve project root before importing utils ────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from utils import paths

IS_WINDOWS = platform.system() == "Windows"
IS_MAC     = platform.system() == "Darwin"
IS_LINUX   = platform.system() == "Linux"


def run(cmd, **kwargs):
    print(">>", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True, **kwargs)


def which(cmd) -> bool:
    """Check if a command exists on PATH."""
    import shutil
    return shutil.which(cmd) is not None


# ── Python dependencies ───────────────────────────────────────────────────────

def setup_venv():
    venv_dir = ROOT / "env"
    if venv_dir.exists():
        print("✓ Virtual environment already exists")
    else:
        print("⬇  Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(venv_dir)])
        print("✓ Virtual environment created")

    # Resolve pip inside venv
    if IS_WINDOWS:
        pip = venv_dir / "Scripts" / "pip.exe"
    else:
        pip = venv_dir / "bin" / "pip"

    print("⬇  Installing Python dependencies...")
    #run([str(pip), "install", "--upgrade", "pip", "-q"])
    run([str(pip), "install", "-r", str(ROOT / "requirements.txt"), "-q"])
    print("✓ Python dependencies installed")


# ── Node / frontend ───────────────────────────────────────────────────────────

def setup_frontend():
    frontend_dir = ROOT / "frontend"
    if not frontend_dir.exists():
        print("⚠  No frontend directory found, skipping.")
        return

    if not which("node"):
        print("✗ Node.js not found. Please install it from https://nodejs.org and re-run setup.")
        sys.exit(1)

    print("⬇  Installing frontend dependencies...")
    subprocess.run(["npm", "install"], cwd=str(frontend_dir), shell=IS_WINDOWS, check=True)
    print("✓ Frontend dependencies installed")


# ── ffmpeg ────────────────────────────────────────────────────────────────────

def install_ffmpeg():
    if which("ffmpeg"):
        print("✓ ffmpeg already on PATH")
        return

    # Check if we already extracted it to bin dir
    local_ffmpeg = paths.BIN_DIR / ("ffmpeg.exe" if IS_WINDOWS else "ffmpeg")
    if local_ffmpeg.exists():
        print("✓ ffmpeg already in bin dir")
        _add_bin_to_path_hint()
        return

    print("⬇  Downloading ffmpeg...")

    if IS_WINDOWS:
        url      = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = paths.BIN_DIR / "ffmpeg.zip"
        run(["curl", "-L", url, "-o", str(zip_path)])
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(paths.BIN_DIR)
        zip_path.unlink()
        ffmpeg_bin_dir = next(paths.BIN_DIR.glob("ffmpeg-*/bin"))
        for f in ffmpeg_bin_dir.iterdir():
            f.rename(paths.BIN_DIR / f.name)
        ffmpeg_bin_dir.parent.rmdir()

    elif IS_MAC:
        if which("brew"):
            run(["brew", "install", "ffmpeg"])
            print("✓ ffmpeg installed via Homebrew")
            return
        else:
            print("✗ Homebrew not found. Install ffmpeg manually: https://ffmpeg.org/download.html")
            sys.exit(1)

    elif IS_LINUX:
        if which("apt-get"):
            run(["sudo", "apt-get", "install", "-y", "ffmpeg"])
        elif which("dnf"):
            run(["sudo", "dnf", "install", "-y", "ffmpeg"])
        else:
            print("✗ Could not detect package manager. Install ffmpeg manually.")
            sys.exit(1)
        print("✓ ffmpeg installed")
        return

    print(f"✓ ffmpeg extracted to {paths.BIN_DIR}")
    _add_bin_to_path_hint()


# ── yt-dlp ────────────────────────────────────────────────────────────────────

def install_ytdlp():
    if which("yt-dlp"):
        print("✓ yt-dlp already on PATH")
        return

    local_ytdlp = paths.BIN_DIR / ("yt-dlp.exe" if IS_WINDOWS else "yt-dlp")
    if local_ytdlp.exists():
        print("✓ yt-dlp already in bin dir")
        _add_bin_to_path_hint()
        return

    print("⬇  Downloading yt-dlp...")

    if IS_WINDOWS:
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    elif IS_MAC:
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos"
    else:
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"

    run(["curl", "-L", url, "-o", str(local_ytdlp)])

    if not IS_WINDOWS:
        local_ytdlp.chmod(0o755)

    print(f"✓ yt-dlp downloaded to {local_ytdlp}")
    _add_bin_to_path_hint()


# ── LLM model ─────────────────────────────────────────────────────────────────

def install_model():
    if paths.MISTRALQ4_PATH.exists():
        print("✓ Model already exists")
        return

    print("⬇  Downloading Mistral model (~4GB, this will take a while)...")
    url = (
        "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
        "/resolve/main/mistral-7b-instruct-v0.2.Q4_0.gguf"
    )
    run(["curl", "-L", "--progress-bar", url, "-o", str(paths.MISTRALQ4_PATH)])
    print("✓ Model downloaded to:", paths.MISTRALQ4_PATH)


# ── .env ──────────────────────────────────────────────────────────────────────

def setup_env():
    env_path = ROOT / ".env"
    if env_path.exists():
        print("✓ .env already exists")
        return
    print("📝 Creating .env...")
    env_path.write_text(
        "PROJECT_ROOT=.\n"
        "ANKI_CONNECT_URL=http://127.0.0.1:8765\n"
    )
    print("✓ .env created")


# ── Launcher scripts ──────────────────────────────────────────────────────────

def create_launchers():
    if IS_WINDOWS:
        start = ROOT / "start.bat"
        start.write_text(
            "@echo off\n"
            "echo Starting Lang Reader...\n"
            "cd /d %~dp0\n"
            "start \"Lang Reader Backend\" cmd /k \".env\\Scripts\\activate && python -m uvicorn backend.main:app --reload\"\n"
            "timeout /t 3 >nul\n"
            "start \"Lang Reader Frontend\" cmd /k \"cd frontend && npm run dev\"\n"
            "timeout /t 3 >nul\n"
            "start http://localhost:5173\n"
        )
        print("✓ Created start.bat")

        stop = ROOT / "stop.bat"
        stop.write_text(
            "@echo off\n"
            "echo Stopping Lang Reader...\n"
            "taskkill /FI \"WINDOWTITLE eq Lang Reader Backend\" /T /F >nul 2>&1\n"
            "taskkill /FI \"WINDOWTITLE eq Lang Reader Frontend\" /T /F >nul 2>&1\n"
            "echo Done.\n"
        )
        print("✓ Created stop.bat")

    else:
        start = ROOT / "start.sh"
        start.write_text(
            "#!/bin/bash\n"
            "cd \"$(dirname \"$0\")\"\n"
            "echo 'Starting Lang Reader...'\n"
            "source env/bin/activate\n"
            "uvicorn backend.main:app --reload &\n"
            "BACKEND_PID=$!\n"
            "sleep 2\n"
            "cd frontend && npm run dev &\n"
            "FRONTEND_PID=$!\n"
            "sleep 2\n"
            f"{'open' if IS_MAC else 'xdg-open'} http://localhost:5173\n"
            "echo \"Backend PID: $BACKEND_PID\"\n"
            "echo \"Frontend PID: $FRONTEND_PID\"\n"
            "echo \"Run stop.sh to shut down.\"\n"
            "echo \"$BACKEND_PID $FRONTEND_PID\" > .pids\n"
        )
        start.chmod(0o755)
        print("✓ Created start.sh")

        stop = ROOT / "stop.sh"
        stop.write_text(
            "#!/bin/bash\n"
            "cd \"$(dirname \"$0\")\"\n"
            "if [ -f .pids ]; then\n"
            "  kill $(cat .pids) 2>/dev/null\n"
            "  rm .pids\n"
            "  echo 'Lang Reader stopped.'\n"
            "else\n"
            "  echo 'No running processes found.'\n"
            "fi\n"
        )
        stop.chmod(0o755)
        print("✓ Created stop.sh")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _add_bin_to_path_hint():
    print(f"  ⚠  Make sure {paths.BIN_DIR} is on your PATH")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n╔══════════════════════════════════╗")
    print("║     SMTK Setup v0.1              ║")
    print(f"║     Platform: {platform.system():<19}║")
    print("╚══════════════════════════════════╝\n")

    setup_env()
    setup_venv()
    setup_frontend()
    install_ffmpeg()
    install_ytdlp()
    install_model()
    create_launchers()

    print("\n╔══════════════════════════════════╗")
    print("║         Setup Complete! ✓        ║")
    print("╚══════════════════════════════════╝\n")

    if paths.BIN_DIR not in [Path(p) for p in os.environ.get("PATH", "").split(os.pathsep)]:
        print(f"⚠  Add to PATH: {paths.BIN_DIR}")
        print("   Restart your terminal after adding it.\n")

    launcher = "start.bat" if IS_WINDOWS else "start.sh"
    print(f"▶  Run  ./{launcher}  to launch Lang Reader")


if __name__ == "__main__":
    main()