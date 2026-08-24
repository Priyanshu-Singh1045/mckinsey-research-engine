-- Phase 5
-- Migration 005: Validation Records

create table if not exists validation_records (
    id uuid primary key default gen_random_uuid(),

    evidence_id uuid references evidence(id)
        on delete cascade,

    method text,

    result text,

    notes text,

    created_at timestamptz default now()
);