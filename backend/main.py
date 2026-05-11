import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import upload, expenses, summary

IS_VERCEL = os.getenv("VERCEL") == "1"
DATA_DIR = Path("/tmp") if IS_VERCEL else Path(__file__).parent / "data"
UPLOADS_DIR = Path("/tmp/uploads") if IS_VERCEL else Path(__file__).parent / "uploads"

app = FastAPI(title="Receipt Expense Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(summary.router, prefix="/api")


@app.on_event("startup")
async def startup():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    expenses_file = DATA_DIR / "expenses.json"
    if not expenses_file.exists():
        expenses_file.write_text("[]", encoding="utf-8")


@app.get("/health", tags=["Health"])
def health_check():
    """서버 상태 확인 엔드포인트"""
    return {"status": "ok", "version": "1.0.0", "environment": "vercel" if IS_VERCEL else "local"}
