from datetime import datetime
from pydantic import BaseModel


class Source(BaseModel):
    source_id: str
    url: str
    title: str
    source_type: str
    publisher: str | None = None
    published_date: str | None = None
    retrieved_at: datetime