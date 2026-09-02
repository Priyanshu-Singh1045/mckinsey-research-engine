from ai.browser.mock_search import MockSearchEngine


search_engine = MockSearchEngine()

results = search_engine.search(
    "Indian electric vehicle market size"
)

print(f"Found {len(results)} results:\n")

for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Type: {result['source_type']}")
    print(f"Publisher: {result['publisher']}")
    print("-" * 60)

assert len(results) > 0

print("\nSearch engine test passed successfully.")