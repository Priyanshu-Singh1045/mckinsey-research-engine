from ai.research.research_agent import ResearchAgent
from ai.schemas.research_task import ResearchTask
from ai.schemas.source import Source


task = ResearchTask(
    task_id="task_001",
    query="What is the current market size and growth of the Indian electric vehicle market?",
    purpose="Understand the size and growth trajectory of the Indian EV market."
)


agent = ResearchAgent()

sources = agent.research(task)


print(f"\nFound {len(sources)} unique sources:\n")

for source in sources:

    assert isinstance(source, Source)
    assert source.url
    assert source.title
    assert source.source_id
    assert source.retrieved_at

    print(f"Source ID: {source.source_id}")
    print(f"Title: {source.title}")
    print(f"URL: {source.url}")
    print(f"Type: {source.source_type}")
    print(f"Publisher: {source.publisher}")
    print(f"Published: {source.published_date}")
    print(f"Retrieved: {source.retrieved_at}")
    print("-" * 60)


assert len(sources) > 0

urls = [source.url for source in sources]

assert len(urls) == len(set(urls))

print("\nResearch Agent test passed successfully.")