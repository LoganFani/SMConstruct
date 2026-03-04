from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services.db_storage import insert_card, get_cards_for_video, delete_card

router = APIRouter()


class CardCreate(BaseModel):
    video_id: str
    word: str
    context: str
    translation: str
    frame_path: Optional[str] = None
    audio_path: Optional[str] = None


class CardResponse(BaseModel):
    id: int
    video_id: str
    word: str
    context: str
    translation: str
    frame_path: Optional[str]
    audio_path: Optional[str]
    created_at: str


@router.post("/", response_model=CardResponse, status_code=201)
def create_card(req: CardCreate):
    card = insert_card(
        req.video_id, req.word, req.context,
        req.translation, req.frame_path, req.audio_path
    )
    return card


@router.get("/{video_id}", response_model=list[CardResponse])
def list_cards(video_id: str):
    return get_cards_for_video(video_id)


@router.delete("/{card_id}", status_code=204)
def remove_card(card_id: int):
    if not delete_card(card_id):
        raise HTTPException(status_code=404, detail="Card not found")