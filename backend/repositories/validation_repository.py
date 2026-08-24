from backend.db.supabase_client import supabase


class ValidationRepository:

    def create_validation(
        self,
        evidence_id: str,
        is_valid: bool,
        credibility_score: float,
        recency_score: float,
        is_duplicate: bool,
        has_conflict: bool,
        reason: str,
    ) -> dict:

        notes = (
            f"is_valid={is_valid}; "
            f"credibility_score={credibility_score}; "
            f"recency_score={recency_score}; "
            f"is_duplicate={is_duplicate}; "
            f"has_conflict={has_conflict}; "
            f"reason={reason}"
        )

        data = {
            "evidence_id": evidence_id,
            "method": "ai_validation",
            "result": str(is_valid),
            "notes": notes,
        }

        response = (
            supabase
            .table("validation_records")
            .insert(data)
            .execute()
        )

        if not response.data:
            raise RuntimeError("Failed to create validation record")

        return response.data[0]

    def get_validations(
        self,
        evidence_id: str,
    ) -> list[dict]:

        response = (
            supabase
            .table("validation_records")
            .select("*")
            .eq("evidence_id", evidence_id)
            .execute()
        )

        return response.data or []