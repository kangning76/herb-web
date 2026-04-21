import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, herbs, recommendations, stats
from app.config import settings

_VERSION_FILE = Path(__file__).parent.parent.parent / "VERSION"
__version__ = _VERSION_FILE.read_text().strip() if _VERSION_FILE.exists() else "0.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(os.path.join(settings.UPLOAD_DIR, "herbs"), exist_ok=True)
    yield


app = FastAPI(title="TCM Herb Encyclopedia", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(herbs.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

upload_path = Path(settings.UPLOAD_DIR)
if upload_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

# Serve Vue SPA dist if it exists (production mode)
dist_path = Path(__file__).parent.parent.parent / "frontend" / "dist"
if dist_path.exists():
    app.mount("/", StaticFiles(directory=str(dist_path), html=True), name="spa")
