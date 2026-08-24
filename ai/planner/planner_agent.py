import json

from ai.llm.gemini import GeminiLLM
from ai.schemas.research_task import ResearchTask


class PlannerAgent:
    def __init__(self):
        self.llm = GeminiLLM()

    def create_plan(self, query: str) -> list[ResearchTask]:
        prompt = f"""
You are a research planning agent.

Your job is to break the user's research question into clear,
logical and independent research tasks.

User research question:
{query}

Create focused research tasks.

Each task must contain:
- task_id: a unique identifier such as task_001
- query: the specific research question to investigate
- purpose: why this research task is needed

Return ONLY valid JSON.

The JSON must be an array in this exact format:

[
    {{
        "task_id": "task_001",
        "query": "Specific research question",
        "purpose": "Purpose of this research task"
    }}
]

Do not include markdown.
Do not include explanations outside the JSON.
"""

        response = self.llm.generate(prompt).strip()

        if response.startswith("```"):
            response = response.replace("```json", "")
            response = response.replace("```", "")
            response = response.strip()

        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError("Planner returned invalid JSON") from e

        if not isinstance(data, list):
            raise ValueError("Planner response must be a JSON list")

        try:
            return [
                ResearchTask.model_validate(task)
                for task in data
            ]
        except Exception as e:
            raise ValueError("Planner returned invalid research tasks") from e