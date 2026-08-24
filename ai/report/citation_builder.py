from ai.schemas.source import Source
from ai.schemas.citation import Citation


class CitationBuilder:

    def build(self, sources: list[Source]) -> list[Citation]:

        citations = []

        seen_sources = set()

        for index, source in enumerate(sources, start=1):

            if source.source_id in seen_sources:
                continue

            seen_sources.add(source.source_id)

            citations.append(
                Citation(
                    citation_id=f"citation_{len(citations) + 1:03d}",
                    source_id=source.source_id,
                    title=source.title,
                    url=source.url,
                    publisher=source.publisher,
                    published_date=source.published_date
                )
            )

        return citations