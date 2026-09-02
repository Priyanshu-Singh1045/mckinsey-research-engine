from datetime import datetime, timezone

from ai.report.citation_builder import CitationBuilder
from ai.schemas.source import Source


sources = [
    Source(
        source_id="source_001",
        url="https://example.com/source-one",
        title="Indian EV Market Report",
        source_type="industry report",
        publisher="Example Research",
        published_date="2025-01-15",
        retrieved_at=datetime.now(timezone.utc)
    ),
    Source(
        source_id="source_002",
        url="https://example.com/source-two",
        title="EV Charging Infrastructure in India",
        source_type="government",
        publisher="Ministry of Heavy Industries",
        published_date="2025-02-10",
        retrieved_at=datetime.now(timezone.utc)
    )
]


builder = CitationBuilder()

citations = builder.build(sources)


print(f"\nGenerated {len(citations)} citations:\n")

for citation in citations:

    print(f"Citation ID: {citation.citation_id}")
    print(f"Source ID: {citation.source_id}")
    print(f"Title: {citation.title}")
    print(f"URL: {citation.url}")
    print(f"Publisher: {citation.publisher}")
    print(f"Published: {citation.published_date}")
    print("-" * 60)


assert len(citations) == len(sources)

for citation in citations:
    assert citation.url
    assert citation.source_id
    assert citation.title


print("\nCitation Builder test passed successfully.")