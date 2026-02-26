import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from backend.services import llama
from pydantic import BaseModel
from utils import paths

router = APIRouter()

MODEL_PATH = str(paths.MISTRALQ4_PATH)
GRAMMAR_PATH = str(paths.LLAMA_GRAMMAR_JSON_PATH)


class TranslateRequest(BaseModel):
    from_lang: str
    to_lang: str
    user_input: str
    context: str

class TranslateResponse(BaseModel):
    original_content: str
    translation: str
    context: str

@router.post("/translate", response_model=TranslateResponse)
def translate(req: TranslateRequest):
    translator = llama.Translator(MODEL_PATH, GRAMMAR_PATH)

    prompt = translator.build_promptv2(req.user_input, req.context, req.from_lang, req.to_lang)
    output = translator.generate_response(prompt=prompt)

    return {"original_content": output['original_content'], "translation" : output['translation'], "context" : req.context}