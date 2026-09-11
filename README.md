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

## 🚀 Run the Project

1. Start the FastAPI backend:
  `uvicorn main:app --reload`

2. Start the Vite frontend:
  `npm run dev`

3. For production deployment on Render:
  `gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

> Use Gunicorn to manage the server process, while Uvicorn runs the FastAPI application itself.

About shutil: it helps clean up temporary files and session artifacts safely after a user interaction ends.
