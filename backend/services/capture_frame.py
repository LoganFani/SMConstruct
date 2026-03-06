import subprocess
from utils import paths

def find_video(video_id: str):
    potential = paths.VIDEO_STORAGE / (video_id + ".mp4")

    if potential.exists():
        return potential
    else:
        raise FileNotFoundError(f"No video found with id= {video_id}")

def capture_frame(video_id: str, time_stamp: float):
    
    video_file = find_video(video_id)

    convert_ts = f"{time_stamp:.2f}".replace('.', '-') #safe file name format
    frame_path = paths.FRAMES_STORAGE / f"{video_id}_{convert_ts}.jpg"

    if frame_path.exists():
        return str(frame_path)
    
    ffmpeg_cmd = [
        str(paths.BIN_DIR / "ffmpeg"),
        "-y",                      # overwrite if exists
        "-ss", str(time_stamp),    # seek to timestamp
        "-i", str(video_file),
        "-frames:v", "1",         # extract one frame
        "-q:v", "2",              # good JPEG quality
        str(frame_path),
    ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed:\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}"
        )

    return str(frame_path)
