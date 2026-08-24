-- Phase 5
-- Migration 003: Sources

create table if not exists sources (
    id uuid primary key default gen_random_uuid(),

    job_id uuid references research_jobs(id)
        on delete cascade,

    url text not null,

    title text,

    fetched_at timestamptz default now(),

    credibility_score numeric
);