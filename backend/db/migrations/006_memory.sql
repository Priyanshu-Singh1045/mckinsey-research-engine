-- Phase 5
-- Migration 006: Persistent Memory / pgvector

create extension if not exists vector;

create table if not exists memory_records (
    id uuid primary key default gen_random_uuid(),

    topic text not null,

    content text not null,

    embedding vector(1536),

    source_evidence_id uuid references evidence(id),

    created_at timestamptz default now()
);