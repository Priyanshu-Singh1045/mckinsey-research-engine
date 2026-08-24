import json

from backend.db.supabase_client import supabase


class ReportRepository:

    def create_report(
        self,
        job_id: str,
        report: dict,
        version: int = 1,
        status: str = "draft",
    ) -> dict:

        content_md = json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )

        data = {
            "job_id": job_id,
            "content_md": content_md,
            "version": version,
            "status": status,
        }

        response = (
            supabase
            .table("reports")
            .insert(data)
            .execute()
        )

        if not response.data:
            raise RuntimeError("Failed to create report")

        return response.data[0]

    def get_reports(
        self,
        job_id: str,
    ) -> list[dict]:

        response = (
            supabase
            .table("reports")
            .select("*")
            .eq("job_id", job_id)
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []