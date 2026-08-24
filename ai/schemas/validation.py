from pydantic import BaseModel


class ValidationResult(BaseModel):
    evidence_id: str
    is_valid: bool
    credibility_score: float
    recency_score: float
    is_duplicate: bool
    has_conflict: bool
    reason: str