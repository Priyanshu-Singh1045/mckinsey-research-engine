from datetime import datetime, timezone

from ai.extraction.extraction_agent import ExtractionAgent
from ai.schemas.source import Source


source = Source(
    source_id="test_source_001",
    url="https://www.ibef.org/industry/electric-vehicle",
    title="Electric Vehicle Industry in India",
    source_type="web",
    publisher="IBEF",
    published_date=None,
    retrieved_at=datetime.now(timezone.utc)
)


agent = ExtractionAgent()

evidence = agent.extract(source)


print(f"\nExtracted {len(evidence)} evidence items:\n")

for item in evidence:

    print(f"Evidence ID: {item.evidence_id}")
    print(f"Claim: {item.claim}")
    print(f"Excerpt: {item.excerpt}")
    print(f"Entity: {item.entity}")
    print(f"Topic: {item.topic}")
    print(f"Relevance: {item.relevance_score}")
    print(f"Source ID: {item.source_id}")
    print("-" * 60)


assert len(evidence) > 0

for item in evidence:
    assert item.source_id == source.source_id
    assert 0 <= item.relevance_score <= 1

print("\nExtraction Agent test passed successfully.")