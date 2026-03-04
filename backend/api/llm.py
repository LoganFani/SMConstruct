from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.llama import get_translator

router = APIRouter()


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
    translator = get_translator()

    prompt = translator.build_promptv2(req.user_input, req.context, req.from_lang, req.to_lang)
    output = translator.generate_response(prompt=prompt)

    if not output:
        raise HTTPException(status_code=500, detail="LLM returned an empty response")

    return {
        "original_content": output.get("original_content", ""),
        "translation": output.get("translation", ""),
        "context": req.context,
    }