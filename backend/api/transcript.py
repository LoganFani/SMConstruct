import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from backend.services.transcript import parse_transcript_to_blocks, format_srt_time, transcript_to_srt

router = APIRouter()

class TranscriptRequest(BaseModel):
    video_id: str
    transcript: str

class TranscriptResponse(BaseModel):
    parsed_srt_path: str

@router.post("/transcript", response_model=TranscriptResponse)
def convert_transcript(req: TranscriptRequest):
    
    try:
        return transcript_to_srt(req.transcript)
    except:
        raise Exception("Could not parse transcript to SRT.") 
