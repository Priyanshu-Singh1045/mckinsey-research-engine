-- Phase 5
-- Migration 002: Planner Tasks

create table if not exists planner_tasks (
    id uuid primary key default gen_random_uuid(),

    job_id uuid references research_jobs(id)
        on delete cascade,

    task_type text not null,

    query text,

    status text not null default 'queued',

    depends_on uuid references planner_tasks(id),

    created_at timestamptz default now()
);