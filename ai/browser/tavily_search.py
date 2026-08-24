import os

from dotenv import load_dotenv
from tavily import TavilyClient

from ai.browser.search import SearchEngine


load_dotenv()


class TavilySearchEngine(SearchEngine):

    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise ValueError("TAVILY_API_KEY is not set")

        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str) -> list[dict]:
        response = self.client.search(
            query=query,
            search_depth="basic",
            max_results=2
        )

        return response.get("results", [])

    def extract(self, urls: list[str]) -> list[dict]:
        response = self.client.extract(urls)

        return response.get("results", [])