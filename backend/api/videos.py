from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from backend.services.ytdlp import download_video

router = APIRouter()

class VideoLoadRequest(BaseModel):
    youtube_url: str

class VideoLoadResponse(BaseModel):
    video_id: str
    status: str

@router.post("/load", response_model=VideoLoadResponse)
def load_video(req: VideoLoadRequest, background_tasks: BackgroundTasks):
    
    try:
        video_id = download_video(req.youtube_url)
        return {"video_id": video_id, "status": "ready"}

    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))