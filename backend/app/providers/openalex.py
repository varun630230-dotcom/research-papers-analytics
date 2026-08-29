import httpx
from app.schemas.responses import Paper
import asyncio

class OpenAlexProvider:
    def __init__(self, email: str = ''):
        self.email = email
        self.headers = {"mailto": email} if email else {}

    async def search_works(self, query: str, per_page: int = 10) -> list[Paper]:
        url = f"https://api.openalex.org/works?search={query}&per_page={per_page}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 429:
                    await asyncio.sleep(1)
                    response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return [self._parse_work(work) for work in data.get("results", [])]
            except Exception as e:
                print(f"OpenAlex API error: {e}")
                return []

    async def get_work(self, work_id: str) -> Paper | None:
        url = f"https://api.openalex.org/works/{work_id}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                return self._parse_work(response.json())
            except Exception as e:
                return None

    def _parse_work(self, work: dict) -> Paper:
        authors = [a.get("author", {}).get("display_name", "") for a in work.get("authorships", [])]
        
        # Abstract inverted index parsing could be added here, leaving empty for simplicity
        abstract = "" 
        
        venue = work.get("primary_location", {}).get("source", {}).get("display_name", "") if work.get("primary_location") and work.get("primary_location").get("source") else ""
        doi = work.get("doi", "").replace("https://doi.org/", "") if work.get("doi") else None
        
        return Paper(
            id=work.get("id", ""),
            title=work.get("title", ""),
            authors=[a for a in authors if a],
            abstract=abstract,
            year=work.get("publication_year", 0),
            venue=venue,
            doi=doi,
            url=work.get("id", ""),
            citation_count=work.get("cited_by_count", 0),
            open_access=work.get("open_access", {}).get("is_oa", False),
            pdf_url=work.get("open_access", {}).get("oa_url", None),
            source="OpenAlex"
        )
