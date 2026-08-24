from pydantic import BaseModel

from ai.schemas.citation import Citation


class LinkedSource(BaseModel):
    title: str
    url: str
    publisher: str | None = None


class LinkedReportItem(BaseModel):
    text: str
    sources: list[LinkedSource] = []


class LinkedReport(BaseModel):
    title: str
    executive_summary: str

    key_findings: list[LinkedReportItem]
    market_signals: list[LinkedReportItem]
    competitor_observations: list[LinkedReportItem]
    implications: list[LinkedReportItem]
    recommendations: list[LinkedReportItem]

    evidence_appendix: list[str]
    citations: list[Citation] = []