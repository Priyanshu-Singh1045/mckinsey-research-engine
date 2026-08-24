-- Phase 5
-- Migration 001: Research Jobs

create extension if not exists pgcrypto;

create table if not exists research_jobs (
    id uuid primary key default gen_random_uuid(),

    brief text not null,

    status text not null check (
        status in (
            'pending',
            'planning',
            'researching',
            'validating',
            'aggregating',
            'reporting',
            'review',
            'completed',
            'failed'
        )
    ),

    created_by uuid references auth.users(id),

    created_at timestamptz default now(),

    updated_at timestamptz default now()
);