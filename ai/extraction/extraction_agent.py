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

        # --------------------------------------------------
        # 1. Extract content from the source
        # --------------------------------------------------
        extracted = self.browser.extract([source.url])

        if not extracted:
            return []

        content = extracted[0].get("raw_content", "")

        if not content:
            return []

        # --------------------------------------------------
        # 2. Build extraction prompt
        # --------------------------------------------------
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

        # --------------------------------------------------
        # 3. Generate response from Gemini
        # --------------------------------------------------
        response = self.llm.generate(prompt)

        if not response:
            raise ValueError(
                "Extraction agent received an empty response from the LLM."
            )

        # --------------------------------------------------
        # 4. Clean Gemini response
        # --------------------------------------------------
        cleaned_response = response.strip()

        # Remove Markdown code fences if Gemini returns:
        #
        # ```json
        # [...]
        # ```
        if cleaned_response.startswith("```"):
            lines = cleaned_response.splitlines()

            if lines and lines[0].strip().startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned_response = "\n".join(lines).strip()

        # --------------------------------------------------
        # 5. Extract the JSON array
        # --------------------------------------------------
        # Sometimes Gemini may return extra text before or
        # after the JSON. Find the first '[' and last ']'.
        start = cleaned_response.find("[")
        end = cleaned_response.rfind("]")

        if start != -1 and end != -1 and start < end:
            cleaned_response = cleaned_response[start:end + 1]

        # --------------------------------------------------
        # 6. Parse JSON
        # --------------------------------------------------
        try:
            data = json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            print("\n--- INVALID GEMINI RESPONSE ---")
            print(repr(cleaned_response))
            print("--- END RESPONSE ---\n")

            raise ValueError(
                "Extraction agent returned invalid JSON."
            ) from e

        # --------------------------------------------------
        # 7. Validate top-level JSON structure
        # --------------------------------------------------
        if not isinstance(data, list):
            raise ValueError(
                "Extraction agent expected a JSON array."
            )

        # --------------------------------------------------
        # 8. Validate evidence items
        # --------------------------------------------------
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

            # Check required fields
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

            # Check claim
            if not str(item["claim"]).strip():
                print(
                    f"Skipping evidence item {index}: "
                    "claim is empty."
                )
                continue

            # Check excerpt
            if not str(item["excerpt"]).strip():
                print(
                    f"Skipping evidence item {index}: "
                    "excerpt is empty."
                )
                continue

            # Check relevance score
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

            # --------------------------------------------------
            # 9. Create Evidence object
            # --------------------------------------------------
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

        # --------------------------------------------------
        # 10. Make sure at least one valid evidence item exists
        # --------------------------------------------------
        if not evidence:
            raise ValueError(
                "Extraction agent returned no valid evidence."
            )

        return evidence