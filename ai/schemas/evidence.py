from pydantic import BaseModel


class Evidence(BaseModel):
    evidence_id: str
    claim: str
    excerpt: str
    entity: str
    topic: str
    relevance_score: float
    source_id: str