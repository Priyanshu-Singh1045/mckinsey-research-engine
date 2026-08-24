from backend.db.supabase_client import supabase


class PlannerTaskRepository:

    def create_task(
        self,
        job_id: str,
        task_type: str,
        query: str,
    ) -> dict:

        response = (
            supabase
            .table("planner_tasks")
            .insert({
                "job_id": job_id,
                "task_type": task_type,
                "query": query,
                "status": "queued",
            })
            .execute()
        )

        if not response.data:
            raise RuntimeError("Failed to create planner task")

        return response.data[0]

    def get_tasks(self, job_id: str) -> list[dict]:

        response = (
            supabase
            .table("planner_tasks")
            .select("*")
            .eq("job_id", job_id)
            .execute()
        )

        return response.data or []

    def update_status(
        self,
        task_id: str,
        status: str,
    ) -> dict:

        response = (
            supabase
            .table("planner_tasks")
            .update({
                "status": status,
            })
            .eq("id", task_id)
            .execute()
        )

        if not response.data:
            raise RuntimeError("Failed to update planner task")

        return response.data[0]