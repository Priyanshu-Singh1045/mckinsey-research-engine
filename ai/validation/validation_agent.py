import json
import logging

from ai.llm.gemini import GeminiLLM
from ai.schemas.evidence import Evidence
from ai.schemas.source import Source
from ai.schemas.validation import ValidationResult

logger = logging.getLogger(__name__)

# Number of evidence items validated in one Gemini request
VALIDATION_BATCH_SIZE = 20


class ValidationAgent:

    def __init__(self, llm=None):
        self.llm = llm or GeminiLLM()

    # -------------------------------------------------------
    # Public Validation Method
    # -------------------------------------------------------

    def validate(
        self,
        evidences: list[Evidence],
        sources: list[Source],
    ) -> list[ValidationResult]:
        """
        Validate evidence in batches to reduce Gemini token usage.
        """

        if not evidences:
            return []

        source_map = {
            source.source_id: source
            for source in sources
        }

        all_results = []

        for start in range(0, len(evidences), VALIDATION_BATCH_SIZE):

            batch = evidences[start:start + VALIDATION_BATCH_SIZE]

            logger.info(
                f"Validating evidence batch "
                f"{start + 1}-{start + len(batch)} "
                f"of {len(evidences)}"
            )

            batch_results = self._validate_batch(
                batch,
                source_map,
            )

            all_results.extend(batch_results)

        logger.info(
            f"Validation completed: {len(all_results)} evidence results."
        )

        return all_results

    # -------------------------------------------------------
    # Batch Validation
    # -------------------------------------------------------

    def _validate_batch(
        self,
        evidences: list[Evidence],
        source_map: dict,
    ) -> list[ValidationResult]:

        evidence_data = []

        for evidence in evidences:

            source = source_map.get(evidence.source_id)

            evidence_data.append(
                {
                    "evidence_id": evidence.evidence_id,
                    "claim": evidence.claim,
                    "excerpt": evidence.excerpt,
                    "entity": evidence.entity,
                    "topic": evidence.topic,
                    "relevance_score": evidence.relevance_score,
                    "source_title": source.title if source else "",
                    "source_type": source.source_type if source else "",
                    "publisher": source.publisher if source else "",
                    "published_date": (
                        source.published_date if source else ""
                    ),
                }
            )

        prompt = f"""
You are a research evidence validation agent.

Evaluate each evidence item using ONLY the supplied information.

Return ONLY valid JSON.

Evidence:
{json.dumps(evidence_data, indent=2)}

Return exactly this structure:

[
  {{
    "evidence_id":"...",
    "is_valid":true,
    "credibility_score":0.85,
    "recency_score":0.90,
    "is_duplicate":false,
    "has_conflict":false,
    "reason":"Short explanation."
  }}
]

Rules:
- Use only supplied evidence.
- Do not invent facts.
- credibility_score must be between 0 and 1.
- recency_score must be between 0 and 1.
- Return one result for every evidence item.
- Return JSON only.
"""

        response = self.llm.generate(prompt)

        cleaned_response = self._clean_response(response)

        try:
            data = json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            logger.error("Invalid validation JSON returned by Gemini.")
            logger.error(cleaned_response)

            raise ValueError(
                "Validation agent returned invalid validation JSON."
            ) from e

        results = []

        for item in data:

            try:
                results.append(
                    ValidationResult(
                        evidence_id=item["evidence_id"],
                        is_valid=bool(item["is_valid"]),
                        credibility_score=max(
                            0.0,
                            min(float(item["credibility_score"]), 1.0),
                        ),
                        recency_score=max(
                            0.0,
                            min(float(item["recency_score"]), 1.0),
                        ),
                        is_duplicate=bool(item["is_duplicate"]),
                        has_conflict=bool(item["has_conflict"]),
                        reason=str(item["reason"]).strip(),
                    )
                )

            except KeyError:
                logger.warning(
                    f"Skipping malformed validation item: {item}"
                )

        return results

    # -------------------------------------------------------
    # Response Cleaner
    # -------------------------------------------------------

    @staticmethod
    def _clean_response(response: str) -> str:

        cleaned = response.strip()

        if cleaned.startswith("```"):
            lines = cleaned.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        start = cleaned.find("[")
        end = cleaned.rfind("]")

        if start != -1 and end != -1:
            cleaned = cleaned[start:end + 1]

        return cleaned
