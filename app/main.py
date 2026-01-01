import os, time
from typing import Optional, List
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .wp_index import WPIndex

load_dotenv()

WP_BASE_URL = os.getenv("WP_BASE_URL", "").rstrip("/")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
API_KEY = os.getenv("API_KEY", "")
INDEX_REFRESH_MINUTES = int(os.getenv("INDEX_REFRESH_MINUTES", "60"))

if not WP_BASE_URL:
    raise RuntimeError("WP_BASE_URL is required in .env")

app = FastAPI(title="Library Navigation Bot", version="0.1.0")

# Only allow requests from your website(s)
if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-API-Key"],
    )

index = WPIndex(WP_BASE_URL)

class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)

class LinkOut(BaseModel):
    title: str
    url: str

class ChatOut(BaseModel):
    reply: str
    links: List[LinkOut] = []

def require_api_key(x_api_key: Optional[str]) -> None:
    # If API_KEY is set, requests must include X-API-Key
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

async def refresh_if_needed():
    now = time.time()
    if not index.docs or (now - index.last_built) > (INDEX_REFRESH_MINUTES * 60):
        await index.rebuild()

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn, x_api_key: Optional[str] = Header(default=None)):
    require_api_key(x_api_key)
    await refresh_if_needed()

    results = index.search(payload.message, top_k=5)
    if not results:
        return ChatOut(
            reply="I couldn’t find a specific page for that. Try: hours, library card, printing, events, or contact.",
            links=[]
        )

    links = [LinkOut(title=r.title or r.url, url=r.url) for r in results]
    return ChatOut(reply="Here are the most relevant pages I found:", links=links)

