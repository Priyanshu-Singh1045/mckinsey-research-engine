from ai.validation.validation_agent import ValidationAgent
from ai.schemas.evidence import Evidence
from ai.schemas.source import Source


source = Source(
    source_id="test_source_001",
    url="https://example.com/india-ev-market",
    title="India Electric Vehicle Market Report",
    source_type="industry report",
    publisher="Example Research",
    published_date="2025-01-15",
    retrieved_at="2026-08-15T10:00:00Z"
)


evidences = [
    Evidence(
        evidence_id="test_source_001_evidence_001",
        claim="The Indian EV market is projected to reach US$ 191.04 billion by 2034.",
        excerpt=(
            "The Indian EV market, valued at US$ 3.71 billion in 2025, "
            "is projected to grow to US$ 191.04 billion by 2034."
        ),
        entity="Indian EV market",
        topic="Market Growth",
        relevance_score=0.98,
        source_id="test_source_001"
    ),

    Evidence(
        evidence_id="test_source_001_evidence_002",
        claim="India has 29,151 public EV charging stations.",
        excerpt=(
            "According to the Ministry of Heavy Industries, "
            "India has 29,151 public charging stations."
        ),
        entity="EV charging infrastructure",
        topic="Infrastructure",
        relevance_score=0.95,
        source_id="test_source_001"
    )
]


agent = ValidationAgent()

results = agent.validate(
    evidences=evidences,
    sources=[source]
)


print(f"\nValidated {len(results)} evidence items:\n")


for result in results:

    print(f"Evidence ID: {result.evidence_id}")
    print(f"Valid: {result.is_valid}")
    print(f"Credibility: {result.credibility_score}")
    print(f"Recency: {result.recency_score}")
    print(f"Duplicate: {result.is_duplicate}")
    print(f"Conflict: {result.has_conflict}")
    print(f"Reason: {result.reason}")
    print("-" * 60)


assert len(results) == len(evidences)

for result in results:
    assert 0 <= result.credibility_score <= 1
    assert 0 <= result.recency_score <= 1


print("\nValidation Agent test passed successfully.")