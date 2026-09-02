from ai.report.report_linker import ReportLinker

from ai.schemas.evidence import Evidence
from ai.schemas.citation import Citation
from ai.schemas.report import Report
from ai.schemas.report_item import ReportItem


evidences = [
    Evidence(
        evidence_id="evidence_001",
        claim="The Indian EV market is growing rapidly.",
        excerpt="The Indian EV market is projected to grow significantly.",
        entity="Indian EV market",
        topic="Market Growth",
        relevance_score=0.95,
        source_id="source_001"
    ),
    Evidence(
        evidence_id="evidence_002",
        claim="India has a large public EV charging network.",
        excerpt="India has thousands of public EV charging stations.",
        entity="EV charging infrastructure",
        topic="Infrastructure",
        relevance_score=0.92,
        source_id="source_002"
    )
]


citations = [
    Citation(
        citation_id="citation_001",
        source_id="source_001",
        title="Indian EV Market Report",
        url="https://example.com/ev-market",
        publisher="Example Research",
        published_date="2025-01-15"
    ),
    Citation(
        citation_id="citation_002",
        source_id="source_002",
        title="EV Charging Infrastructure Report",
        url="https://example.com/charging",
        publisher="Example Organization",
        published_date="2025-02-10"
    )
]


report = Report(
    title="Indian EV Market",
    executive_summary="The Indian EV market is growing.",

    key_findings=[
        ReportItem(
            text="The Indian EV market is growing rapidly.",
            evidence_ids=["evidence_001"]
        )
    ],

    market_signals=[
        ReportItem(
            text="EV charging infrastructure is expanding.",
            evidence_ids=["evidence_002"]
        )
    ],

    competitor_observations=[],

    implications=[
        ReportItem(
            text="The market creates opportunities for EV ecosystem players.",
            evidence_ids=["evidence_001"]
        )
    ],

    recommendations=[
        ReportItem(
            text="Stakeholders should prepare for continued EV market growth.",
            evidence_ids=["evidence_001"]
        )
    ],

    evidence_appendix=[
        "evidence_001",
        "evidence_002"
    ],

    citations=citations
)


linker = ReportLinker()

linked_report = linker.link_report(
    report=report,
    evidences=evidences,
    citations=citations
)


print("\nLINKED REPORT\n")

print(f"Title: {linked_report.title}")


print("\nKEY FINDINGS:")

for item in linked_report.key_findings:

    print(f"\n• {item.text}")

    for source in item.sources:
        print(
            f"  Source: {source.publisher} - "
            f"{source.url}"
        )


print("\nMARKET SIGNALS:")

for item in linked_report.market_signals:

    print(f"\n• {item.text}")

    for source in item.sources:
        print(
            f"  Source: {source.publisher} - "
            f"{source.url}"
        )


print("\nIMPLICATIONS:")

for item in linked_report.implications:

    print(f"\n• {item.text}")

    for source in item.sources:
        print(
            f"  Source: {source.publisher} - "
            f"{source.url}"
        )


print("\nRECOMMENDATIONS:")

for item in linked_report.recommendations:

    print(f"\n• {item.text}")

    for source in item.sources:
        print(
            f"  Source: {source.publisher} - "
            f"{source.url}"
        )


assert len(linked_report.key_findings) == 1

assert len(
    linked_report.key_findings[0].sources
) == 1

assert (
    linked_report.key_findings[0].sources[0].url
    == "https://example.com/ev-market"
)

assert (
    linked_report.key_findings[0].sources[0].title
    == "Indian EV Market Report"
)

assert len(linked_report.market_signals) == 1

assert (
    linked_report.market_signals[0].sources[0].url
    == "https://example.com/charging"
)


print(
    "\nReport Linker typed-model test passed successfully."
)