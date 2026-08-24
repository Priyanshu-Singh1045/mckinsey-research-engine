import json

from ai.browser.tavily_search import TavilySearchEngine
from ai.llm.gemini import GeminiLLM
from ai.schemas.evidence import Evidence
from ai.schemas.source import Source


class ExtractionAgent:

    def __init__(self, llm=None, browser=None):
        self.llm = llm or GeminiLLM()
        self.browser = browser or TavilySearchEngine()

    def extract(self, source: Source) -> list[Evidence]:

        extracted = self.browser.extract([source.url])

        if not extracted:
            return []

        content = extracted[0].get("raw_content", "")

        if not content:
            return []

        prompt = f"""
You are an evidence extraction agent.

Analyze the following source content.

SOURCE ID:
{source.source_id}

SOURCE TITLE:
{source.title}

SOURCE URL:
{source.url}

CONTENT:
{content}

Extract the most useful factual claims from this source.

Return ONLY valid JSON.

Return a JSON array using exactly this structure:

[
    {{
        "claim": "A concise factual claim",
        "excerpt": "A short excerpt supporting the claim",
        "entity": "Main entity discussed",
        "topic": "Research topic",
        "relevance_score": 0.95
    }}
]

Rules:
- Extract only information supported by the provided content.
- Do not invent facts.
- Do not use outside knowledge.
- Every evidence item MUST contain an excerpt.
- The excerpt MUST directly support the claim.
- Keep excerpts short.
- relevance_score must be between 0 and 1.
- Return only JSON.
"""

        response = self.llm.generate(prompt)



        if not response:
            raise ValueError(
                "Extraction agent received an empty response from the LLM."
            )

        cleaned_response = response.strip()

        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.replace("```json", "")
            cleaned_response = cleaned_response.replace("```", "")
            cleaned_response = cleaned_response.strip()

        try:
            data = json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            print("\n--- INVALID GEMINI RESPONSE ---")
            print(cleaned_response)
            print("--- END RESPONSE ---\n")

            raise ValueError(
                "Extraction agent returned invalid JSON."
            ) from e

        if not isinstance(data, list):
            raise ValueError(
                "Extraction agent expected a JSON array."
            )

        evidence = []

        required_fields = [
            "claim",
            "excerpt",
            "entity",
            "topic",
            "relevance_score"
        ]

        for index, item in enumerate(data, start=1):

            if not isinstance(item, dict):
                print(
                    f"Skipping evidence item {index}: "
                    "not a JSON object."
                )
                continue

            missing_fields = [
                field
                for field in required_fields
                if field not in item or item[field] is None
            ]

            if missing_fields:
                print(
                    f"Skipping evidence item {index} "
                    f"because fields are missing: {missing_fields}"
                )
                continue

            if not str(item["claim"]).strip():
                print(
                    f"Skipping evidence item {index}: "
                    "claim is empty."
                )
                continue

            if not str(item["excerpt"]).strip():
                print(
                    f"Skipping evidence item {index}: "
                    "excerpt is empty."
                )
                continue

            try:
                relevance_score = float(
                    item["relevance_score"]
                )

            except (TypeError, ValueError):
                print(
                    f"Skipping evidence item {index}: "
                    "invalid relevance_score."
                )
                continue

            if not 0 <= relevance_score <= 1:
                print(
                    f"Skipping evidence item {index}: "
                    f"relevance_score {relevance_score} "
                    "is outside the 0-1 range."
                )
                continue

            evidence.append(
                Evidence(
                    evidence_id=(
                        f"{source.source_id}_evidence_"
                        f"{len(evidence) + 1:03d}"
                    ),
                    claim=str(item["claim"]).strip(),
                    excerpt=str(item["excerpt"]).strip(),
                    entity=str(item["entity"]).strip(),
                    topic=str(item["topic"]).strip(),
                    relevance_score=relevance_score,
                    source_id=source.source_id
                )
            )

        if not evidence:
            raise ValueError(
                "Extraction agent returned no valid evidence."
            )

        return evidence