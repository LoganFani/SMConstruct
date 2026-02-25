import os
import sys
import subprocess
import hashlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

VIDEO_DIR = Path(os.getenv("VIDEO_STORAGE", "backend/storage/videos"))
SUBS_DIR = Path(os.getenv("SUBS_STORAGE", "backend/storage/subs"))

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
SUBS_DIR.mkdir(parents=True, exist_ok=True)

def has_ytdlp() -> bool:
    try:
        subprocess.run(["yt-dlp", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False
    
def get_video_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]

def download_video(url: str) -> str:
    if not has_ytdlp():
        raise RuntimeError("yt-dlp is not installed")
    
    video_id = get_video_id(url=url)

    for ext in ("mp4", "webm", "mkv"):
        if (VIDEO_DIR / f"{video_id}.{ext}").exists():
            print("Video already cached")
            return video_id
        
    ytdlp_cmd = [
        "yt-dlp",
        "-P", VIDEO_DIR,
        "--ignore-errors",
        "--no-abort-on-error",
        "--sleep-interval", "5",
        url,
    ]



    subprocess.run(ytdlp_cmd, check=True)
    return video_id