from ai.browser.search import SearchEngine


class MockSearchEngine(SearchEngine):

    def search(self, query: str) -> list[dict]:

        return [
            {
                "url": "https://example.com/source1",
                "title": f"Research result for {query}",
                "source_type": "web",
                "publisher": "Example"
            }
        ]