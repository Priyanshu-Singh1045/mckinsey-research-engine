import json

from ai.llm.gemini import GeminiLLM
from ai.schemas.evidence import Evidence
from ai.schemas.validation import ValidationResult
from ai.schemas.research_task import ResearchTask
from ai.schemas.report import Report


class ReportAgent:

    def __init__(self, llm=None):
        self.llm = llm or GeminiLLM()

    def generate_report(
        self,
        tasks: list[ResearchTask],
        evidences: list[Evidence],
        validations: list[ValidationResult],
        citations
    ) -> Report:

        if not evidences:
            raise ValueError("No evidence available for report generation")

        validation_map = {
            validation.evidence_id: validation
            for validation in validations
        }

        report_evidence = []

        for evidence in evidences:

            validation = validation_map.get(evidence.evidence_id)

            if validation and not validation.is_valid:
                continue

            report_evidence.append(
                {
                    "evidence_id": evidence.evidence_id,
                    "claim": evidence.claim,
                    "excerpt": evidence.excerpt,
                    "entity": evidence.entity,
                    "topic": evidence.topic,
                    "relevance_score": evidence.relevance_score,
                    "source_id": evidence.source_id,
                    "validation": {
                        "credibility_score": (
                            validation.credibility_score
                            if validation else None
                        ),
                        "recency_score": (
                            validation.recency_score
                            if validation else None
                        ),
                        "is_duplicate": (
                            validation.is_duplicate
                            if validation else None
                        ),
                        "has_conflict": (
                            validation.has_conflict
                            if validation else None
                        ),
                    }
                }
            )

        if not report_evidence:
            raise ValueError("No valid evidence available for report generation")

        prompt = f"""
You are a senior strategy research analyst.

Create a professional research report based ONLY on the provided
research task and validated evidence.

RESEARCH TASK:

{json.dumps(
    [task.model_dump() for task in tasks],
    indent=2
)}

VALIDATED EVIDENCE:

{json.dumps(report_evidence, indent=2)}

Your report must contain:

1. title
2. executive_summary
3. key_findings
4. market_signals
5. competitor_observations
6. implications
7. recommendations
8. evidence_appendix

IMPORTANT RULES:

- Use ONLY the provided evidence.
- Do not invent facts.
- Do not use outside knowledge.
- Do not create statistics that are not present in the evidence.
- Do not treat unsupported assumptions as facts.
- Recommendations must logically follow from the findings.
- Keep the executive summary concise.
- Key findings should contain the most important facts.
- Market signals should describe important trends visible in the evidence.
- Competitor observations should only be included when supported by the evidence.
- Implications should explain why the findings matter.
- Recommendations should be practical and connected to the evidence.
- Evidence appendix should reference the evidence IDs used.
- Return ONLY valid JSON.
- Do not return Markdown.
- Do not return ```json.
- Do not include explanations outside the JSON.

Return exactly this structure:

{{
    "title": "Research report title",
    "executive_summary": "Concise summary of the research.",
    "key_findings": [
        {{
            "text": "Finding 1",
            "evidence_ids": ["evidence_001"]
        }},
        {{
            "text": "Finding 2",
            "evidence_ids": ["evidence_002"]
        }}
    ],
    "market_signals": [
        {{
            "text": "Market signal 1",
            "evidence_ids": ["evidence_003"]
        }}
    ],
    "competitor_observations": [
        {{
            "text": "Competitor observation 1",
            "evidence_ids": ["evidence_004"]
        }}
    ],
    "implications": [
        {{
            "text": "Strategic implication 1",
            "evidence_ids": ["evidence_001"]
        }}
    ],
    "recommendations": [
        {{
            "text": "Recommendation 1",
            "evidence_ids": ["evidence_001"]
        }}
    ],
    "evidence_appendix": [
        "evidence_001",
        "evidence_002"
    ]
}}
"""

        response = self.llm.generate(prompt)

        try:

            response = response.strip()

            if response.startswith("```"):
                response = response.replace("```json", "")
                response = response.replace("```", "")
                response = response.strip()

            data = json.loads(response)

            report = Report.model_validate(data)

            report.citations = citations

            return report

        except Exception as e:

            raise ValueError(
                "Report agent returned invalid report"
            ) from e