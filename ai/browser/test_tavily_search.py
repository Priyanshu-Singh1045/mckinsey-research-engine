from dotenv import load_dotenv

from ai.browser.tavily_search import TavilySearchEngine


load_dotenv()

search_engine = TavilySearchEngine()

results = search_engine.search(
    "Indian electric vehicle market size"
)

print(f"\nFound {len(results)} results:\n")

for result in results:
    print(f"Title: {result.get('title')}")
    print(f"URL: {result.get('url')}")
    print(f"Content: {result.get('content', '')[:300]}")
    print("-" * 60)

assert len(results) > 0

print("\nTavily search test passed successfully.")