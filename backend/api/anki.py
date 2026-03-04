from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services import anki
from backend.services.db_storage import (
    get_cards_for_video, get_all_videos,
    get_exported_card_ids, record_exports,
)

router = APIRouter()


class ExportRequest(BaseModel):
    video_id: Optional[str] = None
    deck_name: str


class ExportResponse(BaseModel):
    deck_name: str
    exported: int
    skipped_duplicate: int
    skipped_already_exported: int


@router.get("/decks")
def list_decks():
    try:
        return anki.get_decks()
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/export", response_model=ExportResponse)
def export_to_anki(req: ExportRequest):
    try:
        anki.ensure_note_type()
        anki.create_deck(req.deck_name)

        # Gather cards
        if req.video_id:
            all_cards = get_cards_for_video(req.video_id)
        else:
            videos = get_all_videos()
            all_cards = []
            for v in videos:
                all_cards.extend(get_cards_for_video(v["id"]))

        if not all_cards:
            return {
                "deck_name": req.deck_name,
                "exported": 0,
                "skipped_duplicate": 0,
                "skipped_already_exported": 0,
            }

        # Filter out cards already exported to this deck
        all_ids = [c["id"] for c in all_cards]
        already_exported = get_exported_card_ids(all_ids, req.deck_name)
        cards_to_send = [c for c in all_cards if c["id"] not in already_exported]
        skipped_already = len(already_exported)

        if not cards_to_send:
            return {
                "deck_name": req.deck_name,
                "exported": 0,
                "skipped_duplicate": 0,
                "skipped_already_exported": skipped_already,
            }

        # Send to Anki — note_ids is None for Anki-side duplicates
        note_ids = anki.add_notes(req.deck_name, cards_to_send)

        # Record only the ones Anki accepted
        accepted_ids = [
            cards_to_send[i]["id"]
            for i, nid in enumerate(note_ids)
            if nid is not None
        ]
        record_exports(accepted_ids, req.deck_name)

        exported = len(accepted_ids)
        skipped_dupe = len(note_ids) - exported

        return {
            "deck_name": req.deck_name,
            "exported": exported,
            "skipped_duplicate": skipped_dupe,
            "skipped_already_exported": skipped_already,
        }

    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))