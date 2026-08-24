# Meridian — AI Market Research & Strategy Engine

A full-stack, multi-agent market research application. A user submits a
research brief; a planner → researcher → validator → report pipeline
(FastAPI + LangGraph-style agents) gathers and scores evidence from the
web and returns a structured, cited strategy report. The frontend is a
React + Tailwind app with real Supabase authentication.

## Stack

- **Frontend** — React (Vite), Tailwind CSS v4, React Router, Supabase JS client
- **Backend** — FastAPI, Supabase (Postgres + Auth)
- **AI pipeline** — planner / research / validation / report agents (`ai/`)

## Project structure

```
backend/            FastAPI app, API routes, repositories, DB migrations
frontend/vite-project/   React frontend
ai/                  Agent pipeline, schemas, prompts
```

## 1. Backend setup

```bash
cd backend
python -m venv ../venv
source ../venv/bin/activate      # Windows: ..\venv\Scripts\activate
pip install -r requirements.txt
```

Copy the root `.env.example` to `.env` and fill in:

- `GOOGLE_API_KEY`, `TAVILY_API_KEY` — pipeline provider keys
- `SUPABASE_URL` — your Supabase project URL
- `SUPABASE_KEY` — your Supabase **service role** key (backend only —
  this key must never be shipped to the frontend)

Run the migrations in `backend/db/migrations/` against your Supabase
project (SQL editor, in numeric order), then start the API:

```bash
uvicorn backend.main:app --reload --port 8000
```

## 2. Enable Supabase Auth

The app uses real Supabase email/password authentication.

1. In the Supabase dashboard: **Authentication → Providers**, confirm
   Email is enabled.
2. Decide whether email confirmation is required
   (**Authentication → Settings**). The signup page already handles
   both cases (instant session, or "check your email").
3. `research_jobs.created_by` references `auth.users(id)` — this is
   already in the migrations, so jobs are automatically scoped to the
   signed-in user, and the backend enforces that a user can only read
   their own jobs.

## 3. Frontend setup

```bash
cd frontend/vite-project
npm install
cp .env.example .env
```

Fill in `.env`:

- `VITE_SUPABASE_URL` — same Supabase project URL as the backend
- `VITE_SUPABASE_ANON_KEY` — the **anon / public** key from
  **Project Settings → API** (not the service role key)
- `VITE_API_BASE_URL` — where the backend is running
  (`http://localhost:8000` locally)

Then:

```bash
npm run dev
```

Visit `http://localhost:5173`, create an account, and submit a
research brief.

## 4. Deployment

**Frontend** — any static host (Vercel, Netlify, Cloudflare Pages).
Set the three `VITE_*` env vars in the host's dashboard and use
`npm run build` / `dist` as the output.

**Backend** — any Python host that can run `uvicorn`/`gunicorn`
(Render, Railway, Fly.io, a VM). Set `GOOGLE_API_KEY`,
`TAVILY_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY` as environment
variables. Update `VITE_API_BASE_URL` on the frontend to point at the
deployed backend URL, and make sure CORS on the backend allows the
frontend's deployed origin.

## How auth protection works

- The frontend signs users in via Supabase Auth and stores the
  session client-side (`AuthContext`).
- Every API call from the frontend attaches
  `Authorization: Bearer <supabase_access_token>`.
- The backend (`backend/core/auth.py`) verifies that token against
  Supabase on every `/api/research/*` request and rejects missing or
  invalid tokens with `401`.
- Each research job is stamped with the creator's user id; the
  backend returns `403` if a user requests a job they don't own.

## Notes on the research pipeline

`POST /api/research/` runs the full agent pipeline synchronously in a
single request — there's no live progress feed from the backend today.
The frontend's loading screen (`ResearchProgress.jsx`) shows a
staged, time-based animation while it waits for that request to
resolve. If you want real live progress later, that would mean adding
a background job + polling or websocket endpoint on the backend.
