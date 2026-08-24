BACKEND

This folder contains the backend for the AI Market Research & Strategy Engine.

The backend is built using Python and FastAPI. It handles API requests, user authentication, research jobs, and communication between the frontend, database, and AI pipeline.


TECH USED

- Python
- FastAPI
- Supabase
- PostgreSQL
- Google Gemini API
- Tavily API


FOLDER STRUCTURE

backend/

├── api/             API routes
├── core/            Config, authentication and error handling
├── db/              Supabase connection and database files
├── middleware/      Custom middleware
├── repositories/    Database queries
├── services/        Main backend logic
│
├── main.py          Main FastAPI application
└── requirements.txt Python dependencies


HOW TO RUN LOCALLY

1. Create a virtual environment

From the project root, run:

python -m venv .venv


2. Activate the virtual environment

For Windows PowerShell:

.\.venv\Scripts\Activate.ps1


3. Install dependencies

pip install -r backend/requirements.txt


4. Add environment variables

Create a .env file in the project root.

Add your environment variables:

GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key


5. Run the backend

From the project root:

python -m uvicorn backend.main:app --reload


The backend will run at:

http://127.0.0.1:8000


API DOCUMENTATION

FastAPI provides API documentation automatically.

After starting the backend, open:

http://127.0.0.1:8000/docs


MAIN API ROUTES

Research

POST   /api/research
GET    /api/research
GET    /api/research/{job_id}
GET    /api/research/{job_id}/tasks
GET    /api/research/{job_id}/sources
GET    /api/research/{job_id}/evidence
GET    /api/research/{job_id}/validations
GET    /api/research/{job_id}/report


Other Routes

GET    /api/reports/test
GET    /api/evidence/test
GET    /api/feedback/test


HEALTH CHECK

GET /health

This route can be used to check if the backend is running properly.


NOTES

- The .env file is not included in the repository.

- API keys and Supabase credentials should be added using environment variables.

- The AI research pipeline is located in the ai folder and is called from the backend service layer.