from fastapi import FastAPI, BackgroundTasks

app = FastAPI()


'''
app.include_router(videos.router, prefix="/api/video")
app.include_router(transcripts.router, prefix="/api/transcript")
app.include_router(llm.router, prefix="/api/llm")
app.include_router(anki.router, prefix="/api/anki")
app.include_router(frames.router, prefix="/api/video")
'''