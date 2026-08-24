from pydantic import BaseModel


class Citation(BaseModel):
    citation_id: str
    source_id: str
    title: str
    url: str
    publisher: str | None = None
    published_date: str | None = None