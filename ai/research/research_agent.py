from datetime import datetime, timezone
from urllib.parse import urlparse

from ai.browser.tavily_search import TavilySearchEngine
from ai.schemas.research_task import ResearchTask
from ai.schemas.source import Source


class ResearchAgent:

    def __init__(self):
        self.search_engine = TavilySearchEngine()

    def research(self, task: ResearchTask) -> list[Source]:
        results = self.search_engine.search(task.query)

        sources = []
        seen_urls = set()

        for index, result in enumerate(results, start=1):

            url = result.get("url")
            title = result.get("title")

            if not url or not title:
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            source = Source(
                source_id=f"{task.task_id}_source_{len(sources) + 1:03d}",
                url=url,
                title=title,
                source_type=self._classify_source(url),
                publisher=result.get("publisher"),
                published_date=result.get("published_date"),
                retrieved_at=datetime.now(timezone.utc)
            )

            sources.append(source)

        return sources

    def _classify_source(self, url: str) -> str:
        domain = urlparse(url).netloc.lower()

        if ".gov." in domain or domain.endswith(".gov"):
            return "government"

        if ".edu." in domain or domain.endswith(".edu"):
            return "academic"

        if "reuters.com" in domain:
            return "news"

        if "bloomberg.com" in domain:
            return "financial"

        return "web"