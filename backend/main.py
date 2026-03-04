import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import videos, llm, transcript, frames, language_configs, cards, anki
from backend.services.llama import init_translator
from utils import paths


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading LLM model...")
    # Run the blocking model load in a thread so the event loop stays free
    await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: init_translator(
            model_path=str(paths.MISTRALQ4_PATH),
            grammar_path=str(paths.LLAMA_GRAMMAR_JSON_PATH),
        )
    )
    print("LLM model ready.")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(videos.router, prefix="/api/video")
app.include_router(llm.router, prefix="/api/llm")
app.include_router(transcript.router, prefix="/api/transcript")
app.include_router(frames.router, prefix="/api/capture")
app.include_router(language_configs.router, prefix="/api/language-configs")
app.include_router(cards.router, prefix="/api/cards")
app.include_router(anki.router, prefix="/api/anki")

@app.get("/")
def root():
    return "Hello world"