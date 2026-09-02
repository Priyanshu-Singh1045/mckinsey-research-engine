from ai.report.report_agent import ReportAgent

from ai.schemas.evidence import Evidence
from ai.schemas.validation import ValidationResult
from ai.schemas.research_task import ResearchTask
from ai.schemas.citation import Citation


task = ResearchTask(
    task_id="task_001",
    query="What is the current state of the Indian EV market?",
    purpose="Understand the size and growth of the Indian EV market."
)


evidences = [
    Evidence(
        evidence_id="test_source_001_evidence_001",
        claim=(
            "The Indian electric vehicle market is projected "
            "to reach US$ 191.04 billion by 2034."
        ),
        excerpt=(
            "The Indian EV market, valued at US$ 3.71 billion "
            "in 2025, is projected to grow to US$ 191.04 billion "
            "by 2034."
        ),
        entity="Indian EV market",
        topic="Market Growth",
        relevance_score=0.98,
        source_id="test_source_001"
    ),

    Evidence(
        evidence_id="test_source_001_evidence_002",
        claim=(
            "India has 29,151 public EV charging stations."
        ),
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


validations = [
    ValidationResult(
        evidence_id="test_source_001_evidence_001",
        is_valid=True,
        credibility_score=0.85,
        recency_score=0.95,
        is_duplicate=False,
        has_conflict=False,
        reason="The claim is directly supported by the excerpt."
    ),

    ValidationResult(
        evidence_id="test_source_001_evidence_002",
        is_valid=True,
        credibility_score=0.90,
        recency_score=0.95,
        is_duplicate=False,
        has_conflict=False,
        reason="The claim is supported by the provided excerpt."
    )
]

citations = [
    Citation(
        citation_id="citation_001",
        source_id="source_001",
        title="Indian EV Market Report",
        url="https://example.com/source-one",
        publisher="Example Research",
        published_date="2025-01-15"
    ),
    Citation(
        citation_id="citation_002",
        source_id="source_002",
        title="EV Charging Infrastructure in India",
        url="https://example.com/source-two",
        publisher="Ministry of Heavy Industries",
        published_date="2025-02-10"
    )
]

agent = ReportAgent()


report = agent.generate_report(
    tasks=[task],
    evidences=evidences,
    validations=validations,
    citations=citations
)


print("\nREPORT GENERATED SUCCESSFULLY\n")

print(f"Title:\n{report.title}\n")

print("Executive Summary:")
print(report.executive_summary)
print()

print("Key Findings:")
for finding in report.key_findings:
    print(f"- {finding}")
print()

print("Market Signals:")
for signal in report.market_signals:
    print(f"- {signal}")
print()

print("Competitor Observations:")
for observation in report.competitor_observations:
    print(f"- {observation}")
print()

print("Implications:")
for implication in report.implications:
    print(f"- {implication}")
print()

print("Recommendations:")
for recommendation in report.recommendations:
    print(f"- {recommendation}")
print()

print("Evidence Appendix:")
for evidence_id in report.evidence_appendix:
    print(f"- {evidence_id}")
print()

print("Report Agent test passed successfully.")