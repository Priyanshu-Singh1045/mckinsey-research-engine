-- Phase 5
-- Migration 004: Evidence

create table if not exists evidence (
    id uuid primary key default gen_random_uuid(),

    job_id uuid references research_jobs(id)
        on delete cascade,

    source_id uuid references sources(id),

    claim text not null,

    quote text,

    confidence numeric
        check (confidence between 0 and 1),

    status text default 'pending',

    created_at timestamptz default now()
);