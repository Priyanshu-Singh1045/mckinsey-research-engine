from pydantic import BaseModel

from ai.schemas.citation import Citation
from ai.schemas.report_item import ReportItem


class Report(BaseModel):
    title: str
    executive_summary: str
    key_findings: list[ReportItem]
    market_signals: list[ReportItem]
    competitor_observations: list[ReportItem]
    implications: list[ReportItem]
    recommendations: list[ReportItem]
    evidence_appendix: list[str]
    citations: list[Citation] = []