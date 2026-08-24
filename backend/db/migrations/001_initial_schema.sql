create extension if not exists vector;


create table research_jobs (
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


create table planner_tasks (
    id uuid primary key default gen_random_uuid(),
    job_id uuid references research_jobs(id) on delete cascade,
    task_type text not null,
    query text,
    status text not null default 'queued',
    depends_on uuid references planner_tasks(id),
    created_at timestamptz default now()
);


create table sources (
    id uuid primary key default gen_random_uuid(),
    job_id uuid references research_jobs(id) on delete cascade,
    url text not null,
    title text,
    fetched_at timestamptz default now(),
    credibility_score numeric
);


create table evidence (
    id uuid primary key default gen_random_uuid(),
    job_id uuid references research_jobs(id) on delete cascade,
    source_id uuid references sources(id),
    claim text not null,
    quote text,
    confidence numeric check (
        confidence between 0 and 1
    ),
    status text default 'pending',
    created_at timestamptz default now()
);


create table validation_records (
    id uuid primary key default gen_random_uuid(),
    evidence_id uuid references evidence(id) on delete cascade,
    method text,
    result text,
    notes text,
    created_at timestamptz default now()
);


create table memory_records (
    id uuid primary key default gen_random_uuid(),
    topic text not null,
    content text not null,
    embedding vector(1536),
    source_evidence_id uuid references evidence(id),
    created_at timestamptz default now()
);


create table reports (
    id uuid primary key default gen_random_uuid(),
    job_id uuid references research_jobs(id) on delete cascade,
    content_md text not null,
    version int default 1,
    status text default 'draft',
    created_at timestamptz default now()
);


create table feedback (
    id uuid primary key default gen_random_uuid(),
    report_id uuid references reports(id) on delete cascade,
    reviewer_id uuid references auth.users(id),
    comment text,
    action text,
    created_at timestamptz default now()
);


create index idx_evidence_job
on evidence(job_id);


create index idx_tasks_job
on planner_tasks(job_id);


create index idx_memory_embedding
on memory_records
using ivfflat (embedding vector_cosine_ops);