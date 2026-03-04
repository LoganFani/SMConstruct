from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.services.ytdlp import download_video
from backend.services.db_storage import insert_video, get_all_videos, get_video
from utils import paths

router = APIRouter()


class VideoLoadRequest(BaseModel):
    youtube_url: str
    title: str
    from_lang: str
    to_lang: str


class VideoLoadResponse(BaseModel):
    video_id: str
    status: str
    video_url: str


class VideoRecord(BaseModel):
    id: str
    title: str
    from_lang: str
    to_lang: str
    created_at: str


@router.post("/load", response_model=VideoLoadResponse)
def load_video(req: VideoLoadRequest):
    try:
        video_id = download_video(req.youtube_url)
        insert_video(video_id, req.title, req.from_lang, req.to_lang)
        return {
            "video_id": video_id,
            "status": "ready",
            "video_url": f"http://127.0.0.1:8000/api/video/stream/{video_id}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[VideoRecord])
def list_videos():
    return get_all_videos()


@router.get("/{video_id}", response_model=VideoRecord)
def get_video_record(video_id: str):
    record = get_video(video_id)
    if not record:
        raise HTTPException(status_code=404, detail="Video not found")
    return record


@router.get("/stream/{video_id}")
def stream_video(video_id: str):
    video_path = paths.VIDEO_STORAGE / f"{video_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(video_path, media_type="video/mp4")