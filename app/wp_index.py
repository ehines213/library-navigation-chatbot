import re, time
from dataclasses import dataclass
from typing import List, Dict, Any
import httpx

WORD_RE = re.compile(r"[a-zA-Z0-9']+")

def tokenize(text: str) -> List[str]:
    return [t.lower() for t in WORD_RE.findall(text or "")]

def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()

@dataclass
class PageDoc:
    title: str
    url: str
    excerpt: str
    tokens: List[str]

class WPIndex:
    def __init__(self, wp_base_url: str):
        self.wp_base_url = wp_base_url.rstrip("/")
        self.docs: List[PageDoc] = []
        self.last_built = 0.0

    async def fetch_pages(self) -> List[Dict[str, Any]]:
        url = f"{self.wp_base_url}/wp-json/wp/v2/pages"
        params = {"per_page": 100, "status": "publish"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()

    async def rebuild(self) -> None:
        pages = await self.fetch_pages()
        docs: List[PageDoc] = []
        for p in pages:
            title = (p.get("title", {}) or {}).get("rendered", "") or ""
            link = p.get("link", "") or ""
            excerpt = (p.get("excerpt", {}) or {}).get("rendered", "") or ""
            excerpt_txt = re.sub(r"<[^>]+>", " ", excerpt)
            tokens = tokenize(title + " " + excerpt_txt)
            docs.append(PageDoc(
                title=clean_text(title),
                url=link,
                excerpt=clean_text(excerpt_txt),
                tokens=tokens
            ))
        self.docs = docs
        self.last_built = time.time()

    def search(self, query: str, top_k: int = 5) -> List[PageDoc]:
        q_tokens = tokenize(query)
        if not q_tokens or not self.docs:
            return []
        qset = set(q_tokens)

        scored = []
        for d in self.docs:
            overlap = sum(1 for t in d.tokens if t in qset)
            title_boost = sum(2 for t in tokenize(d.title) if t in qset)
            score = overlap + title_boost
            if score > 0:
                scored.append((score, d))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:top_k]]

