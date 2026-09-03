import json
import logging

from ai.browser.tavily_search import TavilySearchEngine
from ai.llm.gemini import GeminiLLM
from ai.schemas.evidence import Evidence
from ai.schemas.source import Source

logger = logging.getLogger(__name__)

# Number of sources processed in one Gemini request
BATCH_SIZE = 5


class ExtractionAgent:

    def __init__(self, llm=None, browser=None):
        self.llm = llm or GeminiLLM()
        self.browser = browser or TavilySearchEngine()

    # -------------------------------------------------------
    # Existing single-source extraction (kept for compatibility)
    # -------------------------------------------------------

    def extract(self, source: Source) -> list[Evidence]:
        return self.extract_batch([source])

    # -------------------------------------------------------
    # New batch extraction
    # -------------------------------------------------------

    def extract_batch(self, sources: list[Source]) -> list[Evidence]:
        """
        Extract evidence from multiple sources in a single Gemini call.

        This reduces API usage significantly while keeping the output format
        identical.
        """

        urls = [source.url for source in sources]

        extracted = self.browser.extract(urls)

        if not extracted:
            return []

        source_blocks = []

        for source, extracted_item in zip(sources, extracted):
            content = extracted_item.get("raw_content", "")

            if not content:
                continue

            source_blocks.append(
                f"""
SOURCE_ID: {source.source_id}
TITLE: {source.title}
URL: {source.url}

CONTENT:
{content[:6000]}
"""
            )

        if not source_blocks:
            return []

        prompt = f"""
You are an evidence extraction agent.

Analyze ALL of the following sources.

Return ONLY valid JSON.

Return a JSON array using exactly this structure:

[
  {{
    "source_id": "source_001",
    "claim": "A concise factual claim",
    "excerpt": "Short supporting excerpt",
    "entity": "Main entity",
    "topic": "Research topic",
    "relevance_score": 0.95
  }}
]

Rules:
- Extract 2-5 factual claims from each source.
- Every evidence item MUST contain source_id.
- Excerpts must come directly from the content.
- Do not invent facts.
- Return ONLY JSON.

{"".join(source_blocks)}
"""

        response = self.llm.generate(prompt)

        if not response:
            raise ValueError(
                "Extraction agent received an empty response from Gemini."
            )

        cleaned_response = self._clean_response(response)

        try:
            data = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logger.error("Invalid Gemini JSON response during extraction.")
            logger.error(cleaned_response)
            raise ValueError("Extraction agent returned invalid JSON.") from e

        if not isinstance(data, list):
            raise ValueError("Expected JSON array from extraction agent.")

        source_lookup = {
            source.source_id: source for source in sources
        }

        evidences = []

        for item in data:

            if not isinstance(item, dict):
                continue

            required_fields = [
                "source_id",
                "claim",
                "excerpt",
                "entity",
                "topic",
                "relevance_score",
            ]

            if any(field not in item for field in required_fields):
                continue

            source = source_lookup.get(item["source_id"])

            if source is None:
                continue

            try:
                score = float(item["relevance_score"])
            except Exception:
                continue

            score = max(0.0, min(score, 1.0))

            evidence_id = (
                f"{source.source_id}_evidence_{len(evidences)+1:03d}"
            )

            evidences.append(
                Evidence(
                    evidence_id=evidence_id,
                    claim=item["claim"].strip(),
                    excerpt=item["excerpt"].strip(),
                    entity=item["entity"].strip(),
                    topic=item["topic"].strip(),
                    relevance_score=score,
                    source_id=source.source_id,
                )
            )

        if not evidences:
            raise ValueError(
                "Extraction agent returned no valid evidence."
            )

        logger.info(
            f"Extraction completed: {len(evidences)} evidence items "
            f"from {len(sources)} sources."
        )

        return evidences

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
