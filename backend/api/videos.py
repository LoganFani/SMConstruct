from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from backend.services.ytdlp import download_video
from backend.services.db_storage import (
    insert_video, get_all_videos, get_video,
    delete_video, delete_cards_for_video
)
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


@router.get("/stream/{video_id}")
def stream_video(video_id: str):
    video_path = paths.VIDEO_STORAGE / f"{video_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(video_path, media_type="video/mp4")


@router.get("/{video_id}", response_model=VideoRecord)
def get_video_record(video_id: str):
    record = get_video(video_id)
    if not record:
        raise HTTPException(status_code=404, detail="Video not found")
    return record


@router.delete("/{video_id}", status_code=204)
def remove_video(video_id: str, full: bool = False):
    if not get_video(video_id):
        raise HTTPException(status_code=404, detail="Video not found")

    # Always delete video + transcript files
    for f in [
        paths.VIDEO_STORAGE / f"{video_id}.mp4",
        paths.SUBS_STORAGE  / f"{video_id}.json",
        paths.SUBS_STORAGE  / f"{video_id}.vtt",
    ]:
        if f.exists():
            f.unlink()

    if full:
        # Delete all associated card files from disk
        cards = delete_cards_for_video(video_id)
        for card in cards:
            for file_field in ("frame_path", "audio_path"):
                fp = card.get(file_field)
                if fp:
                    p = Path(fp)
                    if p.exists():
                        p.unlink()

    delete_video(video_id)