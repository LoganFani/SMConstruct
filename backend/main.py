from fastapi import FastAPI, BackgroundTasks
from backend.api import videos, llm, transcript

app = FastAPI()

app.include_router(videos.router, prefix="/api/video")
app.include_router(llm.router, prefix="/api/llm")
app.include_router(transcript.router, prefix="/api/transcript")

@app.get("/")
def root():
    return "Hello world"

'''
app.include_router(anki.router, prefix="/api/anki")
app.include_router(frames.router, prefix="/api/video")
'''