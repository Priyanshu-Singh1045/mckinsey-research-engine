-- Phase 5
-- Migration 007: Reports

create table if not exists reports (
    id uuid primary key default gen_random_uuid(),

    job_id uuid references research_jobs(id)
        on delete cascade,

    content_md text not null,

    version int default 1,

    status text default 'draft',

    created_at timestamptz default now()
);