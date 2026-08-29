import httpx
from app.schemas.responses import Paper

class CrossrefProvider:
    async def search_works(self, query: str, rows: int = 5) -> list[Paper]:
        url = f"https://api.crossref.org/works?query={query}&rows={rows}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                items = data.get('message', {}).get('items', [])
                return [self._parse_item(item) for item in items]
            except Exception as e:
                print(f"Crossref API error: {e}")
                return []

    def _parse_item(self, item: dict) -> Paper:
        title = item.get('title', [''])[0]
        authors_data = item.get('author', [])
        authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_data]
        doi = item.get('DOI', '')
        venue = item.get('container-title', [''])[0]
        
        date_parts = item.get('published', {}).get('date-parts', [[0]])
        year = date_parts[0][0] if date_parts and date_parts[0] else 0
        
        return Paper(
            id=doi,
            title=title,
            authors=authors,
            abstract="",
            year=year,
            venue=venue,
            doi=doi,
            url=f"https://doi.org/{doi}" if doi else "",
            citation_count=item.get('is-referenced-by-count', 0),
            open_access=False,
            pdf_url=None,
            source="Crossref"
        )
