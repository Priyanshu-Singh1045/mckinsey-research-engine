from backend.db.supabase_client import supabase


class EvidenceRepository:

    def create_evidence(
        self,
        job_id: str,
        source_id: str,
        claim: str,
        quote: str | None = None,
        confidence: float | None = None,
    ) -> dict:

        data = {
            "job_id": job_id,
            "source_id": source_id,
            "claim": claim,
            "quote": quote,
            "confidence": confidence,
            "status": "pending",
        }

        response = (
            supabase
            .table("evidence")
            .insert(data)
            .execute()
        )

        if not response.data:
            raise RuntimeError("Failed to create evidence")

        return response.data[0]

    def get_evidence(
        self,
        job_id: str,
    ) -> list[dict]:

        response = (
            supabase
            .table("evidence")
            .select("*")
            .eq("job_id", job_id)
            .execute()
        )

        return response.data or []