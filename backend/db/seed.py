from backend.db.supabase_client import supabase


def seed_research_job():
    job = {
        "brief": "Market sizing for EV battery recycling in Southeast Asia",
        "status": "pending",
    }

    response = (
        supabase
        .table("research_jobs")
        .insert(job)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Failed to create sample research job")

    created_job = response.data[0]

    print("Sample research job created successfully.")
    print(f"Job ID: {created_job['id']}")
    print(f"Status: {created_job['status']}")


if __name__ == "__main__":
    seed_research_job()