import json

from ai.llm.gemini import GeminiLLM
from ai.schemas.evidence import Evidence
from ai.schemas.source import Source
from ai.schemas.validation import ValidationResult


class ValidationAgent:

    def __init__(self, llm=None):
        self.llm = llm or GeminiLLM()

    def validate(
        self,
        evidences: list[Evidence],
        sources: list[Source]
    ) -> list[ValidationResult]:

        if not evidences:
            return []

        source_map = {
            source.source_id: source
            for source in sources
        }

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
                    "source_id": evidence.source_id,
                    "source_title": source.title if source else None,
                    "source_url": source.url if source else None,
                    "source_type": source.source_type if source else None,
                    "publisher": source.publisher if source else None,
                    "published_date": source.published_date if source else None,
                }
            )

        prompt = f"""
You are a research evidence validation agent.

Your job is to evaluate research evidence extracted from web sources.

Review each evidence item carefully.

EVIDENCE:

{json.dumps(evidence_data, indent=2)}

For each evidence item evaluate:

1. is_valid
   - True if the claim is supported by the provided excerpt.
   - False if the claim is unsupported, misleading, or cannot be determined.

2. credibility_score
   - Score from 0 to 1.
   - Consider the type and publisher of the source.
   - Do not use outside knowledge to verify the claim.

3. recency_score
   - Score from 0 to 1.
   - Use the published date when available.
   - More recent information should generally receive a higher score.
   - If the publication date is unavailable, use a reasonable neutral score.

4. is_duplicate
   - True if another evidence item makes essentially the same claim.
   - Otherwise false.

5. has_conflict
   - True if another evidence item contradicts this claim.
   - Otherwise false.

6. reason
   - Give a short explanation for the validation result.

IMPORTANT RULES:

- Use only the information provided above.
- Do not invent facts.
- Do not perform outside research.
- Return one validation result for every evidence item.
- credibility_score must be between 0 and 1.
- recency_score must be between 0 and 1.
- Return ONLY valid JSON.
- Do not use Markdown.
- Do not include ```json.
- Do not include any explanation outside the JSON.

Return exactly this structure:

[
    {{
        "evidence_id": "evidence_001",
        "is_valid": true,
        "credibility_score": 0.85,
        "recency_score": 0.90,
        "is_duplicate": false,
        "has_conflict": false,
        "reason": "The claim is directly supported by the provided excerpt."
    }}
]
"""

        response = self.llm.generate(prompt)

        try:
            response = response.strip()

            if response.startswith("```"):
                response = response.replace("```json", "")
                response = response.replace("```", "")
                response = response.strip()

            data = json.loads(response)

            results = []

            for item in data:

                result = ValidationResult(
                    evidence_id=item["evidence_id"],
                    is_valid=bool(item["is_valid"]),
                    credibility_score=float(item["credibility_score"]),
                    recency_score=float(item["recency_score"]),
                    is_duplicate=bool(item["is_duplicate"]),
                    has_conflict=bool(item["has_conflict"]),
                    reason=item["reason"]
                )

                results.append(result)

            return results

        except Exception as e:

            raise ValueError(
                "Validation agent returned invalid validation results"
            ) from e