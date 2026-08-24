-- Phase 5
-- Migration 009: Indexes

create index if not exists idx_evidence_job
    on evidence(job_id);

create index if not exists idx_tasks_job
    on planner_tasks(job_id);

create index if not exists idx_memory_embedding
    on memory_records
    using ivfflat (embedding vector_cosine_ops);