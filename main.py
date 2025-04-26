from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from routes.api import router
from core.db import get_db

app = FastAPI(
    title="MotivationAI API",
    description="API for habit tracking and gamification",
    version="1.0.0"
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

