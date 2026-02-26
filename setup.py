# setup.py
import subprocess
from utils import paths


def run(cmd):
    print(">>", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)


def has(cmd):
    try:
        subprocess.run([cmd, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def install_ffmpeg():
    if has("ffmpeg"):
        print("✅ ffmpeg already installed")
        return

    print("⬇ Installing ffmpeg...")
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = paths.BIN_DIR / "ffmpeg.zip"

    run(["curl", "-L", url, "-o", zip_path])
    run(["tar", "-xf", zip_path, "-C", paths.BIN_DIR])

    ffmpeg_folder = next(paths.BIN_DIR.glob("ffmpeg-*"))
    ffmpeg_bin = ffmpeg_folder / "bin"

    print(f"✅ ffmpeg extracted to {ffmpeg_bin}")
    print("⚠ Add this directory to PATH:")
    print(ffmpeg_bin)


def install_ytdlp():
    try:
        run(["yt-dlp", "--version"])
        print("✅ yt-dlp already installed")
        return
    except Exception:
        pass

    print("⬇ Installing yt-dlp...")
    ytdlp_path = paths.BIN_DIR / "yt-dlp.exe"

    run([
        "curl", "-L",
        "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
        "-o", ytdlp_path
    ])

    print(f"✅ yt-dlp installed to {ytdlp_path}")
    print("⚠ Add backend/bin to PATH")


def install_model():
    model_url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_0.gguf"

    if paths.MISTRALQ4_PATH.exists():
        print("✅ Model already exists")
        return

    print("⬇ Downloading model (this may take a while)...")
    run([
        "curl", "-L",
        model_url,
        "-o", paths.MISTRALQ4_PATH
    ])

    print("✅ Model downloaded to:", paths.MISTRALQ4_PATH)


def main():
    print("\n --- Lang APP Installer ---\n")

    install_ffmpeg()
    install_ytdlp()
    install_model()

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print(f"Add to PATH: {paths.BIN_DIR}")
    print("Restart terminal after PATH change.")


if __name__ == "__main__":
    main()