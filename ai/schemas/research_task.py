from pydantic import BaseModel


class ResearchTask(BaseModel):
    task_id: str
    query: str
    purpose: str