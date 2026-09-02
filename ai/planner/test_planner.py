from ai.planner.planner_agent import PlannerAgent
from ai.schemas.research_task import ResearchTask


planner = PlannerAgent()

query = "Analyze the Indian electric vehicle market"

tasks = planner.create_plan(query)

print(f"\nGenerated {len(tasks)} research tasks:\n")

for task in tasks:
    assert isinstance(task, ResearchTask)

    print(f"Task ID: {task.task_id}")
    print(f"Query: {task.query}")
    print(f"Purpose: {task.purpose}")
    print("-" * 60)

print("\nPlanner test passed successfully.")