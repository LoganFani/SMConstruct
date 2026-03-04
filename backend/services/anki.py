import base64
import json
from pathlib import Path
from typing import Any
import urllib.request
import urllib.error
from utils import paths


def _request(action: str, **params) -> Any:
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(
        paths.ANKI_CONNECT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except urllib.error.URLError:
        raise ConnectionError(
            "Could not connect to AnkiConnect. Make sure Anki is open "
            "and the AnkiConnect add-on is installed."
        )

    if data.get("error"):
        raise RuntimeError(f"AnkiConnect error: {data['error']}")

    return data["result"]


def get_decks() -> list[str]:
    return _request("deckNames")


def create_deck(deck_name: str) -> None:
    _request("createDeck", deck=deck_name)


def ensure_note_type() -> None:
    """Create the LangReader note type if it doesn't exist yet."""
    existing = _request("modelNames")
    if "LangReader" in existing:
        return

    _request(
        "createModel",
        modelName="LangReader",
        inOrderFields=["Word", "Translation", "Context", "Audio", "Frame"],
        css="""
            .card { font-family: sans-serif; text-align: center; }
            .word { font-size: 2em; font-weight: bold; margin-bottom: 8px; }
            .translation { font-size: 1.4em; color: #555; margin-bottom: 12px; }
            .context { font-size: 0.9em; color: #888; font-style: italic; margin-bottom: 12px; }
            img { max-width: 100%; border-radius: 6px; margin-bottom: 8px; }
        """,
        cardTemplates=[
            {
                "Name": "LangReader Card",
                "Front": """
                    <div class="word">{{Word}}</div>
                    <div class="context">{{Context}}</div>
                    {{Audio}}
                    {{Frame}}
                """,
                "Back": """
                    {{FrontSide}}
                    <hr>
                    <div class="translation">{{Translation}}</div>
                """,
            }
        ],
    )


def _encode_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def store_media(file_path: str) -> str:
    """Store a file in Anki's media collection and return its filename."""
    p = Path(file_path)
    data = _encode_file(file_path)
    _request("storeMediaFile", filename=p.name, data=data)
    return p.name


def add_notes(deck_name: str, cards: list[dict]) -> list[int]:
    """
    Add a list of card dicts to the given deck.
    Each card should have: word, translation, context,
    frame_path (optional), audio_path (optional).
    Returns list of created note IDs.
    """
    notes = []
    for card in cards:
        frame_field = ""
        if card.get("frame_path"):
            try:
                fname = store_media(card["frame_path"])
                frame_field = f'<img src="{fname}">'
            except Exception:
                pass

        audio_field = ""
        if card.get("audio_path"):
            try:
                fname = store_media(card["audio_path"])
                audio_field = f"[sound:{fname}]"
            except Exception:
                pass

        notes.append({
            "deckName": deck_name,
            "modelName": "LangReader",
            "fields": {
                "Word": card["word"],
                "Translation": card["translation"],
                "Context": card.get("context", ""),
                "Audio": audio_field,
                "Frame": frame_field,
            },
            "options": {"allowDuplicate": False},
            "tags": ["lang_reader"],
        })

    return _request("addNotes", notes=notes)