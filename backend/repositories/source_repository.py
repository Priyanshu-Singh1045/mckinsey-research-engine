from backend.db.supabase_client import supabase


class SourceRepository:

    def create_source(
        self,
        job_id: str,
        url: str,
        title: str | None = None,
        fetched_at: str | None = None,
    ) -> dict:

        data = {
            "job_id": job_id,
            "url": url,
            "title": title,
        }

        if fetched_at:
            data["fetched_at"] = fetched_at

        response = (
            supabase
            .table("sources")
            .insert(data)
            .execute()
        )

        if not response.data:
            raise RuntimeError("Failed to create source")

        return response.data[0]

    def get_sources(self, job_id: str) -> list[dict]:

        response = (
            supabase
            .table("sources")
            .select("*")
            .eq("job_id", job_id)
            .execute()
        )

        return response.data or []