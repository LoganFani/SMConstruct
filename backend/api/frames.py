from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from backend.services.capture_frame import capture_frame
from backend.services.capture_audio import capture_audio

router = APIRouter()


class FrameRequest(BaseModel):
    video_id: str
    time_stamp: float

class FrameResponse(BaseModel):
    frame_path: str


class AudioRequest(BaseModel):
    video_id: str
    start: float
    end: float

class AudioResponse(BaseModel):
    audio_path: str


@router.post("/frame", response_model=FrameResponse)
def get_video_frame(req: FrameRequest):
    try:
        frame_path = capture_frame(req.video_id, req.time_stamp)
        return {"frame_path": frame_path}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audio", response_model=AudioResponse)
def get_audio_clip(req: AudioRequest):
    try:
        audio_path = capture_audio(req.video_id, req.start, req.end)
        return {"audio_path": audio_path}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/frame-file/{file_path:path}")
def serve_frame(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Frame not found")
    return FileResponse(path, media_type="image/jpeg")


@router.get("/audio-file/{file_path:path}")
def serve_audio(file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(path, media_type="audio/mpeg")