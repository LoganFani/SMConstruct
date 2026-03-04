import subprocess
from utils import paths


def find_video(video_id: str):
    potential = paths.VIDEO_STORAGE / (video_id + ".mp4")
    if potential.exists():
        return potential
    raise FileNotFoundError(f"No video found with id= {video_id}")


def capture_audio(video_id: str, start: float, end: float) -> str:
    video_file = find_video(video_id)

    duration = round(end - start, 3)

    start_str = f"{start:.2f}".replace(".", "-")
    end_str   = f"{end:.2f}".replace(".", "-")
    audio_path = paths.AUDIO_STORAGE / f"{video_id}_{start_str}_{end_str}.mp3"

    if audio_path.exists():
        return str(audio_path)

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(start),
        "-i", str(video_file),
        "-t", str(duration),
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "2",
        str(audio_path),
    ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed:\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}"
        )

    return str(audio_path)