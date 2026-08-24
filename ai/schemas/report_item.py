from pydantic import BaseModel


class ReportItem(BaseModel):
    text: str
    evidence_ids: list[str] = []