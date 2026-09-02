from ai.pipeline.research_pipeline import ResearchPipeline


query = """
Analyze the Indian electric vehicle market, including market size,
government policies, charging infrastructure, consumer adoption,
and major competitors.
"""


pipeline = ResearchPipeline()

result = pipeline.run(query)

report = result.report
linked_report = result.linked_report


print("\n")
print("=" * 70)
print("FINAL RESEARCH REPORT")
print("=" * 70)


print(f"\nTITLE:\n{report.title}")


print("\nEXECUTIVE SUMMARY:")
print(report.executive_summary)


print("\nKEY FINDINGS:")

for finding in report.key_findings:

    print(f"\n- {finding.text}")

    print(
        f"  Evidence IDs: "
        f"{finding.evidence_ids}"
    )


print("\nMARKET SIGNALS:")

for signal in report.market_signals:

    print(f"\n- {signal.text}")

    print(
        f"  Evidence IDs: "
        f"{signal.evidence_ids}"
    )


print("\nCOMPETITOR OBSERVATIONS:")

if report.competitor_observations:

    for observation in report.competitor_observations:

        print(f"\n- {observation.text}")

        print(
            f"  Evidence IDs: "
            f"{observation.evidence_ids}"
        )

else:

    print("No competitor observations available.")


print("\nIMPLICATIONS:")

for implication in report.implications:

    print(f"\n- {implication.text}")

    print(
        f"  Evidence IDs: "
        f"{implication.evidence_ids}"
    )


print("\nRECOMMENDATIONS:")

for recommendation in report.recommendations:

    print(f"\n- {recommendation.text}")

    print(
        f"  Evidence IDs: "
        f"{recommendation.evidence_ids}"
    )


print("\nEVIDENCE APPENDIX:")

for evidence_id in report.evidence_appendix:

    print(f"- {evidence_id}")


print("\n")
print("=" * 70)
print("LINKED REPORT SOURCES")
print("=" * 70)


print("\nKEY FINDINGS:")

for finding in linked_report.key_findings:

    print(f"\n• {finding.text}")

    if finding.sources:

        for source in finding.sources:

            print(
                f"  Source: "
                f"{source.publisher or source.title}"
            )

            print(
                f"  URL: {source.url}"
            )

    else:

        print("  No linked source found.")


print("\nMARKET SIGNALS:")

for signal in linked_report.market_signals:

    print(f"\n• {signal.text}")

    if signal.sources:

        for source in signal.sources:

            print(
                f"  Source: "
                f"{source.publisher or source.title}"
            )

            print(
                f"  URL: {source.url}"
            )

    else:

        print("  No linked source found.")


print("\nCOMPETITOR OBSERVATIONS:")

if linked_report.competitor_observations:

    for observation in linked_report.competitor_observations:

        print(f"\n• {observation.text}")

        if observation.sources:

            for source in observation.sources:

                print(
                    f"  Source: "
                    f"{source.publisher or source.title}"
                )

                print(
                    f"  URL: {source.url}"
                )

        else:

            print("  No linked source found.")

else:

    print("No competitor observations available.")


print("\nIMPLICATIONS:")

for implication in linked_report.implications:

    print(f"\n• {implication.text}")

    if implication.sources:

        for source in implication.sources:

            print(
                f"  Source: "
                f"{source.publisher or source.title}"
            )

            print(
                f"  URL: {source.url}"
            )

    else:

        print("  No linked source found.")


print("\nRECOMMENDATIONS:")

for recommendation in linked_report.recommendations:

    print(f"\n• {recommendation.text}")

    if recommendation.sources:

        for source in recommendation.sources:

            print(
                f"  Source: "
                f"{source.publisher or source.title}"
            )

            print(
                f"  URL: {source.url}"
            )

    else:

        print("  No linked source found.")


print("\n")
print("=" * 70)
print("ALL CITATIONS")
print("=" * 70)


for citation in report.citations:

    print(f"\n[{citation.citation_id}]")
    print(f"Title: {citation.title}")
    print(f"Publisher: {citation.publisher}")
    print(f"URL: {citation.url}")


print("\n")
print("=" * 70)
print("PIPELINE TEST PASSED SUCCESSFULLY")
print("=" * 70)