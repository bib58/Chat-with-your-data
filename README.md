# Conversational Analytics Dashboard

Live demo: [data-chit-chat.vercel.app](https://data-chit-chat.vercel.app/)

Chat with your data using natural language. Upload a CSV, Excel, or JSON file, or
connect to a SQL Server database, then ask analytical questions without writing
SQL or Python.

## Features

### Data exploration

- Upload CSV, XLSX, and JSON datasets.
- Connect to a live SQL Server database with a SQLAlchemy connection string.
- Ask questions in plain English and receive a generated answer.
- Display query results as formatted tables.
- Automatically generate bar, line, pie, or scatter charts when a visualization
  helps explain the result.
- View the generated SQL and copy it for inspection or reuse.
- Copy table results as JSON.
- Export the conversation and insights as a PDF through the browser print dialog.
- Responsive interface with a mobile sidebar and loading/error states.

### Safety and privacy

- Detects prompt injection, jailbreak attempts, system commands, destructive SQL,
  and unrelated questions before query generation.
- Allows only single-statement, read-only `SELECT` queries against known tables.
- Adds a default limit of 50 rows to generated SQLite and SQL Server queries when
  the query does not already specify a limit.
- Sends only a small sample of the dataset to the LLM for schema analysis and
  query generation; data queries execute on the backend.
- Sanitizes answers and table values by removing dangerous HTML, server paths,
  API keys, email addresses, and payment-card data.
- Displays at most 200 result rows in the response.
- Deletes uploaded files and their generated SQLite databases when the browser
  session ends.

### Observability and feedback

- Shows prompt, completion, reasoning, and total token usage when the provider
  returns usage metadata.
- Supports optional per-million-token pricing so estimated costs are calculated
  only when configured; otherwise cost remains unavailable rather than guessed.
- Records LangSmith traces for the request and its LangGraph stages, including
  input validation, schema analysis, query generation, SQL validation,
  execution, response formatting, and output sanitization.
- Redacts local paths and database connection strings from trace inputs/outputs.
- Lets users upvote or downvote AI answers and optionally provide a reason.
- Stores one upserted feedback record per message in the Neon PostgreSQL
  `user_feedback` table when `DATABASE_URL` is configured.

## LLM benchmarking

The `LLM Benchmarking` directory contains the text-to-SQL evaluation workflow.
It builds a golden question set from IPL data covering 2021–2024 and compares
candidate models using the LLM-stats leaderboard as a reference:

- Grok 4.5
- Gemini 3.8 Flash
- GPT-5.6 Terra
- Kimi K3
- Claude Sonnet 5

## Technology stack

### Frontend

- React
- Vite
- Tailwind CSS
- Recharts
- Axios
- `react-markdown` and `remark-gfm`

### Backend

- FastAPI
- LangGraph and LangChain
- Google Gemini through `langchain-google-genai`
- Pandas
- SQLAlchemy and SQLGlot
- SQLite for uploaded datasets
- SQL Server support through `pymssql`
- Neon PostgreSQL for answer feedback
- LangSmith for tracing

## Run locally

### Prerequisites

- Node.js and npm
- Python 3.13+
- A Google Gemini API key

### 1. Configure environment variables

Copy [.env.example](./.env.example) to `.env` and set at least:

```env
GOOGLE_API_KEY=your-google-api-key
```

For feedback persistence, also set a backend-only Neon connection string:

```env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

Never commit `.env` files, API keys, database URLs, or other credentials.

### 2. Start the backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. Verify it with:

```text
GET http://localhost:8000/health
```

### 3. Start the frontend

In a second terminal:

```powershell
npm install
npm run dev
```

The Vite development server uses `http://localhost:8000` by default. To use a
different backend, set `VITE_API_URL` in the frontend environment.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload a CSV, XLSX, or JSON file |
| `POST` | `/connect` | Validate and inspect a SQL Server connection |
| `POST` | `/chat` | Generate and execute a safe analytical query |
| `POST` | `/cleanup` | Remove an uploaded dataset and its local database |
| `POST` | `/feedback` | Save or update answer feedback |

## Deployment

### Render backend

The included [render.yaml](./render.yaml) configures the backend as a Python web
service. Render should provide:

- `GOOGLE_API_KEY`
- `GEMINI_MODEL`
- `CORS_ORIGINS`, including the deployed frontend origin
- `DATABASE_URL` for Neon feedback storage
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT`
- `LANGSMITH_TRACING=true`
- `LANGSMITH_TRACING_V2=true`

The production process is:

```text
gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

After deployment, verify `https://<render-service>/health` returns:

```json
{"status":"ok"}
```

### Vercel frontend

Set `VITE_API_URL` to the deployed Render service URL and redeploy. Production
builds fail clearly when this variable is missing instead of sending API
requests to the frontend host.

## Screenshots

<img src="desc_1.png" alt="Conversational analytics dashboard" />

![alt text](image.png)

![alt text](image-1.png)

![alt text](image-2.png)

