import httpx
import asyncio
from app.schemas.responses import Paper

class SemanticScholarProvider:
    def __init__(self, api_key: str = ''):
        self.headers = {"x-api-key": api_key} if api_key else {}

    async def search_papers(self, query: str, limit: int = 10, fields: str = 'title,authors,abstract,year,venue,externalIds,citationCount,isOpenAccess,openAccessPdf,publicationTypes') -> list[Paper]:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&fields={fields}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(url, headers=self.headers)
                    if response.status_code == 429:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    response.raise_for_status()
                    data = response.json()
                    return [self._parse_paper(p) for p in data.get("data", [])]
                except Exception as e:
                    print(f"Semantic Scholar API error: {e}")
            return []

    async def get_paper(self, paper_id: str) -> Paper | None:
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}?fields=title,authors,abstract,year,venue,externalIds,citationCount,isOpenAccess,openAccessPdf"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return self._parse_paper(response.json())
            except:
                return None

    def _parse_paper(self, paper: dict) -> Paper:
        authors = [a.get("name", "") for a in paper.get("authors", [])]
        doi = paper.get("externalIds", {}).get("DOI", None)
        pdf_url = paper.get("openAccessPdf", {}).get("url") if paper.get("openAccessPdf") else None
        return Paper(
            id=paper.get("paperId", ""),
            title=paper.get("title", ""),
            authors=authors,
            abstract=paper.get("abstract", "") or "",
            year=paper.get("year") or 0,
            venue=paper.get("venue", ""),
            doi=doi,
            url=paper.get("url", f"https://semanticscholar.org/paper/{paper.get('paperId')}"),
            citation_count=paper.get("citationCount", 0),
            open_access=paper.get("isOpenAccess", False),
            pdf_url=pdf_url,
            source="Semantic Scholar"
        )
