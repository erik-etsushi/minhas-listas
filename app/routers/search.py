import re
import httpx
from fastapi import APIRouter, Query
from ..schemas import SearchResult

router = APIRouter(prefix="/api/search", tags=["search"])


def _imdb_poster(url: str) -> str:
    """Resize IMDB image to poster size (~300px wide)."""
    if not url:
        return ""
    return re.sub(r"\._V1_.*\.jpg$", "._V1_UX300_.jpg", url)


async def _buscar_imdb(q: str, qid: str) -> list[SearchResult]:
    """Search movies or series via IMDB suggestion API (no key required)."""
    url = f"https://sg.media-imdb.com/suggestion/x/{q}.json"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        data = r.json()
    results = []
    for item in data.get("d", []):
        if item.get("qid") != qid:
            continue
        poster = _imdb_poster((item.get("i") or {}).get("imageUrl", ""))
        results.append(SearchResult(
            titulo=item.get("l", ""),
            ano=item.get("y"),
            poster_url=poster,
        ))
    return results


async def _buscar_livros(q: str) -> list[SearchResult]:
    url = "https://openlibrary.org/search.json"
    params = {"q": q, "limit": 15, "fields": "title,author_name,first_publish_year,cover_i"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        data = r.json()
    results = []
    for doc in data.get("docs", []):
        cover_i = doc.get("cover_i")
        poster = f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg" if cover_i else ""
        autor = ", ".join((doc.get("author_name") or [])[:2])
        results.append(SearchResult(
            titulo=doc.get("title", ""),
            ano=doc.get("first_publish_year"),
            autor=autor,
            poster_url=poster,
        ))
    return results


@router.get("/", response_model=list[SearchResult])
async def search(
    q: str = Query(..., min_length=1),
    tipo: str = Query(..., pattern="^(filmes|series|livros)$"),
):
    if tipo == "filmes":
        return await _buscar_imdb(q, "movie")
    if tipo == "series":
        return await _buscar_imdb(q, "tvSeries")
    return await _buscar_livros(q)
