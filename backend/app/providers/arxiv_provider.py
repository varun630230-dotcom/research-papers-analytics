import httpx
from bs4 import BeautifulSoup
from app.schemas.responses import Paper

class ArxivProvider:
    async def search_papers(self, query: str, max_results: int = 5) -> list[Paper]:
        url = f"https://export.arxiv.org/api/query?search_query=all:{query}&max_results={max_results}"
        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'xml')
                entries = soup.find_all('entry')
                return [self._parse_entry(entry) for entry in entries]
            except Exception as e:
                print(f"arXiv API error: {e}")
                return []

    def _parse_entry(self, entry) -> Paper:
        title = entry.find('title').text.strip().replace('\n', ' ')
        authors = [author.find('name').text for author in entry.find_all('author')]
        summary = entry.find('summary').text.strip().replace('\n', ' ')
        published = entry.find('published').text
        year = int(published[:4]) if published else 0
        link = entry.find('id').text
        arxiv_id = link.split('/abs/')[-1]
        pdf_link = entry.find('link', title='pdf')
        pdf_url = pdf_link['href'] if pdf_link else None

        return Paper(
            id=arxiv_id,
            title=title,
            authors=authors,
            abstract=summary,
            year=year,
            venue="arXiv",
            doi=f"10.48550/arXiv.{arxiv_id}",
            url=link,
            citation_count=0,
            open_access=True,
            pdf_url=pdf_url,
            source="arXiv"
        )
