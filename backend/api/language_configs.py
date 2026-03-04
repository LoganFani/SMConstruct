from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.db_storage import (
    insert_language_config,
    get_all_language_configs,
    delete_language_config,
)

router = APIRouter()


class LanguageConfigCreate(BaseModel):
    name: str
    from_lang: str
    to_lang: str


class LanguageConfigResponse(BaseModel):
    id: int
    name: str
    from_lang: str
    to_lang: str
    created_at: str


@router.post("/", response_model=LanguageConfigResponse, status_code=201)
def create_language_config(req: LanguageConfigCreate):
    created = insert_language_config(req.name, req.from_lang, req.to_lang)
    return created


@router.get("/", response_model=list[LanguageConfigResponse])
def list_language_configs():
    return get_all_language_configs()


@router.delete("/{config_id}", status_code=204)
def remove_language_config(config_id: int):
    if not delete_language_config(config_id):
        raise HTTPException(status_code=404, detail="Language config not found")