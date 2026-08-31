# Conversational Analytics Dashboard 📊

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![React](https://img.shields.io/badge/React-19-61dafb.svg?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688.svg?logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-ff69b4.svg)

A premium, full-stack conversational analytics platform that allows users to interact with their data using natural language. Whether you are uploading a CSV/Excel/JSON file or connecting directly to a live SQL Server database, this application empowers you to ask questions, receive intelligent summaries, view tabular data, and see dynamically generated charts—all powered by a highly optimized LangGraph Agent and Google Gemini.

## ✨ Key Features

- **🗣️ Natural Language Querying:** Ask complex questions about your data in plain English. No SQL or Python knowledge required.
- **🔌 Multi-Source Data Integration:** 
  - Upload static datasets (`.csv`, `.xlsx`, `.json`).
  - Connect directly to live **SQL Server** databases via connection strings.
- **🧠 Intelligent Agent Pipeline:** 
  - Powered by **LangGraph** and **Gemini** (`gemini-3.6-flash` for high-speed reasoning).
  - Automatically decides whether to generate T-SQL (for SQL Server) or SQLite queries based on the data source.
  - Makes heuristic decisions on when and how to chart the data based on the result set.
- **⚡ Hyper-Optimized Backend:**
  - **Schema Caching:** Prevents redundant database scanning by caching table schemas in memory, dramatically reducing latency.
  - **Single LLM Call:** Combines SQL generation, visualization decisions, and natural language summarization into a single structured LLM call to save time and API costs.
- **💎 Premium Glassmorphic UI:**
  - Built with React and Tailwind CSS v4.
  - Features a rich dark mode (`slate-950`), animated gradient background orbs, frosted glass panels (`backdrop-blur`), and fluid micro-animations.
  - Renders markdown, syntax-highlighted SQL, interactive Recharts, and data tables beautifully.
- **📄 Export to PDF:** Easily export your chat history and generated insights to PDF for reporting.

## 🛠️ Technology Stack

### Frontend
- **Framework:** React 19 + Vite
- **Styling:** Tailwind CSS v4 (Custom UI with Glassmorphism)
- **Charting:** Recharts (Responsive bar, line, pie, and scatter charts)
- **Icons & Typography:** Lucide React, Google Fonts ('Inter')
- **Markdown Processing:** `react-markdown`, `remark-gfm`

### Backend
- **Framework:** FastAPI + Uvicorn
- **Agent Orchestration:** LangGraph + LangChain
- **LLM:** `langchain-google-genai`
- **Data Processing & Execution:** Pandas, SQLAlchemy (SQL Server & SQLite dialects)

## 💡 Problems Solved

1. **Democratizing Data Access:** Analysts and business users often face bottlenecks when querying databases because they lack SQL expertise. This tool translates intent into optimized SQL, making data accessible to everyone.
2. **Reducing AI Latency:** Traditional AI SQL agents use complex, multi-step ReAct loops that are slow and expensive. This implementation solves this by using **Schema Caching** and a **Single Structured Output** LLM call, reducing a typically 15-second process down to a few seconds.
3. **Automated Visualization:** Instead of just dumping raw data tables, the agent intelligently analyzes the shape of the SQL execution result and automatically generates the appropriate `Recharts` configuration to visualize the insight immediately.
4. **The Python backend uses SQLAlchemy to execute the generated SQL.**
> result = pd.read_sql(state["sql_query"], engine)

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Google Gemini API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the backend directory and add your API key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   *The backend runs on `http://localhost:8000`*

### Frontend Setup
1. Navigate to the root directory (or `src` depending on your setup).
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open the application in your browser and start chatting with your data!

## 📁 Project Structure

```text
tapu/
├── backend/               
│   ├── main.py            # FastAPI entry point & REST endpoints
│   ├── agent.py           # LangGraph workflow & LLM logic
│   ├── models.py          # Pydantic models for structured output
│   └── uploads/           # Temporary storage for uploaded CSV/Excel/JSON files
├── src/                   
│   ├── App.jsx            # Main Chat & Dashboard Layout
│   ├── components/        
│   │   ├── Sidebar.jsx       # Data connection & upload UI
│   │   ├── ChatInterface.jsx # Main chat interaction area
│   │   └── MessageBubble.jsx # Renders markdown, tables, and charts
│   ├── index.css          # Tailwind base styles and custom animations
│   └── main.jsx           # React entry point
├── package.json           
└── vite.config.js         
```

---
*Powered by LangGraph & Gemini. Built for high-performance conversational analytics.*
