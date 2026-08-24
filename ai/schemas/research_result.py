from pydantic import BaseModel

from ai.schemas.report import Report
from ai.schemas.linked_report import LinkedReport
from ai.schemas.research_task import ResearchTask
from ai.schemas.source import Source
from ai.schemas.evidence import Evidence
from ai.schemas.validation import ValidationResult


class ResearchResult(BaseModel):
    report: Report
    linked_report: LinkedReport
    tasks: list[ResearchTask]
    sources: list[Source]
    evidences: list[Evidence]
    validations: list[ValidationResult]