from ai.schemas.evidence import Evidence
from ai.schemas.citation import Citation
from ai.schemas.report import Report
from ai.schemas.report_item import ReportItem
from ai.schemas.linked_report import (
    LinkedReport,
    LinkedReportItem,
    LinkedSource
)


class ReportLinker:

    def __init__(self):
        pass

    def _build_maps(
        self,
        evidences: list[Evidence],
        citations: list[Citation]
    ):
        evidence_map = {
            evidence.evidence_id: evidence
            for evidence in evidences
        }

        citation_map = {
            citation.source_id: citation
            for citation in citations
        }

        return evidence_map, citation_map

    def link_item(
        self,
        item: ReportItem,
        evidence_map: dict,
        citation_map: dict
    ) -> LinkedReportItem:

        sources = []

        for evidence_id in item.evidence_ids:

            evidence = evidence_map.get(evidence_id)

            if not evidence:
                continue

            citation = citation_map.get(evidence.source_id)

            if not citation:
                continue

            source = LinkedSource(
                title=citation.title,
                url=citation.url,
                publisher=citation.publisher
            )

            if source not in sources:
                sources.append(source)

        return LinkedReportItem(
            text=item.text,
            sources=sources
        )

    def link_report(
        self,
        report: Report,
        evidences: list[Evidence],
        citations: list[Citation]
    ) -> LinkedReport:

        evidence_map, citation_map = self._build_maps(
            evidences,
            citations
        )

        return LinkedReport(
            title=report.title,
            executive_summary=report.executive_summary,

            key_findings=[
                self.link_item(
                    item,
                    evidence_map,
                    citation_map
                )
                for item in report.key_findings
            ],

            market_signals=[
                self.link_item(
                    item,
                    evidence_map,
                    citation_map
                )
                for item in report.market_signals
            ],

            competitor_observations=[
                self.link_item(
                    item,
                    evidence_map,
                    citation_map
                )
                for item in report.competitor_observations
            ],

            implications=[
                self.link_item(
                    item,
                    evidence_map,
                    citation_map
                )
                for item in report.implications
            ],

            recommendations=[
                self.link_item(
                    item,
                    evidence_map,
                    citation_map
                )
                for item in report.recommendations
            ],

            evidence_appendix=report.evidence_appendix,

            citations=report.citations
        )