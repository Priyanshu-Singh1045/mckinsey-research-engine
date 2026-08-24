-- Phase 5
-- Migration 008: Feedback

create table if not exists feedback (
    id uuid primary key default gen_random_uuid(),

    report_id uuid references reports(id)
        on delete cascade,

    reviewer_id uuid references auth.users(id),

    comment text,

    action text,

    created_at timestamptz default now()
);