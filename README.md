## Conversational Analytics Dashboard 📊

## [https://data-chit-chat.vercel.app/](https://data-chit-chat.vercel.app/)

This application lets users explore their data using natural language. Users can upload CSV, Excel, or JSON files or connect to a live SQL Server database, then ask questions, view summaries, inspect table data, and generate charts from the results.

## ✨ Key Features

- **LLM Guardrails:**
  - Validates input for Prompt injection and jailbreak patterns.
  - Ensures generated SQL stays read-only and targets valid tables.
  - Sanitizes output and redacts sensitive information.
  - Helps prevent HTML/JS injection and XSS-style payloads.

- **Optimized Backend:**
  - Sends only the top three rows of the dataset to the third-party LLM to protect user privacy and minimize data exposure.
  - Uses SQLAlchemy to run generated SQL queries efficiently.
  - Caches table schema information to reduce repeated scans/latency and improve performance.

- **Session Cleanup:** Removes uploaded user files from the backend after the session ends to keep the environment clean and secure.
- **Natural Language Querying:** Ask questions in plain English without writing SQL or Python code.
- **Multi-Source Data Integration:**
  - Upload static datasets such as CSV, XLSX, and JSON files.
  - Connect to live SQL Server databases using connection strings.
- **PDF Export:** Export chat history and generated insights as a PDF report.

---

#### LLM Benchmarking

> Used **LLM-stats** leader-boards to evaluate reliable models for text-to-sql

EValuated upon IPL dataset from 2021-2024 by generating 20-sql questions as golden-dataset
with models:
- Grok 4.5
- Gemini 3.8 Flash
- GPT-5.6 Terra
- Kimi K3
- Claude Sonnet 5

---

## 🛠️ Technology Stack

### Frontend
- **Framework:** React + Tailwind CSS
- **Charting:** Recharts
- **Markdown Processing:** react-markdown, remark-gfm

### Backend
- **Framework:** FastAPI
- **Agent Orchestration:** LangGraph + LangChain
- **LLM:** langchain-google-genai
- **Data Processing & Execution:** Pandas, SQLAlchemy, SQL Server, SQLite

---

<img src='desc_1.png'>

---

For production deployment on Render:
  `gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

> Use Gunicorn to manage the server process, while Uvicorn runs the FastAPI application itself.

About shutil: it helps clean up temporary files and session artifacts safely after a user interaction ends.

### Environment and deployment

Copy [.env.example](./.env.example) to a local environment file for development. Do not
commit `.env` files or API keys.

For the Render backend, set `GOOGLE_API_KEY`, `CORS_ORIGINS` (including the deployed
frontend origin), `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and `DATABASE_URL` in the
Render dashboard. `DATABASE_URL` must be the Neon PostgreSQL connection string and must
remain backend-only; never expose it through Vite or commit it to `.env`.
The included [render.yaml](./render.yaml) uses `backend` as the service root and binds
Gunicorn to Render's `$PORT`. After deployment, verify `https://<render-service>/health`
returns `{"status":"ok"}`.

For the Vercel frontend, set `VITE_API_URL` to the deployed Render service URL and
redeploy. A production build without this variable fails clearly instead of sending
requests to the frontend host.

### Response feedback

AI text responses expose upvote and downvote controls. Feedback is stored in Neon
PostgreSQL in the `user_feedback` table, with one upserted row per `message_id`.
The backend creates the table on startup when `DATABASE_URL` is configured. The
`POST /feedback` endpoint accepts the question, answer, session ID, message ID,
`feedback_type` (`upvote` or `downvote`), and an optional `feedback_reason`.
Feedback storage failures return a clear API error without interrupting chat.

To configure Neon locally, copy [.env.example](./.env.example) to `.env`, replace
the placeholder `DATABASE_URL` with the connection string from the Neon dashboard,
and start the backend. The existing SQLite databases used for uploaded datasets
remain unchanged.

### LangSmith tracing

Each `/chat` request creates a `User Query Received` parent trace. The existing
LangGraph nodes are instrumented as child spans for input validation, dataset schema
generation, query/schema preparation, SQL validation, SQL execution, final answer
generation, and response sanitization. Gemini's LangChain invocation remains nested
inside the query-generation span and reports provider-supplied token usage when
available. Costs are reported only when the optional per-million-token pricing
environment variables are configured; otherwise the cost is `null`, not estimated.

---
