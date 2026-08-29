# Conversational Analytics Dashboard

This document outlines the implementation plan for the full-stack Conversational Analytics Dashboard you requested. The application will allow users to upload datasets or connect databases, ask natural language questions, and receive detailed answers, data tables, and dynamically generated charts, powered by a LangGraph Agent.

## User Review Required

> [!IMPORTANT]
> Please review the architecture and design decisions below. If you approve, I will begin building the frontend components and backend API.

## Open Questions

> [!WARNING]
> 1. **LLM Choice**: You mentioned Gemini or Groq. I will set up the project using **Gemini** since you are currently using the Gemini 3.1 Pro model. Is that okay, or do you specifically want Groq? If so, you will need to provide an API key later.
> 2. **Database Support**: Do you want to support specific databases (e.g., PostgreSQL, MySQL, SQLite) for the database connection feature, or should we focus just on CSV/Excel uploads for the MVP?
> 3. **PDF Generation**: I will use `reportlab` or a similar Python library to generate the PDF of the queries. Does that work for you?

## Architecture & Technology Stack

### Frontend (React + Vite + Tailwind CSS)
- **Framework**: React 19 + Vite (Already initialized)
- **Styling**: Tailwind CSS v4 (Already initialized)
- **State Management & API**: React Hooks + `axios`
- **Charting**: `recharts` (for simple, responsive, and beautiful React charts)
- **Icons**: `lucide-react`

### Backend (Python + FastAPI)
- **Framework**: FastAPI + Uvicorn
- **Data Processing**: Pandas
- **Agent Orchestration**: LangGraph + LangChain
- **LLM**: `langchain-google-genai` (for Gemini)
- **File Handling**: `python-multipart` (for CSV/Excel uploads)
- **PDF Generation**: `reportlab`

## Proposed Changes

We will restructure the project slightly to accommodate both frontend and backend in the same workspace.

### Workspace Structure
```
tapu/
├── backend/               # New Python backend directory
│   ├── main.py            # FastAPI entry point
│   ├── agent.py           # LangGraph workflow definition
│   ├── tools.py           # Pandas/SQL execution tools
│   ├── models.py          # Pydantic models for API
│   └── requirements.txt   # Python dependencies
├── src/                   # Existing React frontend directory
│   ├── App.jsx            # Main Chat & Dashboard UI
│   ├── components/        # UI components (Upload, ChatBubble, Chart, Table)
│   ├── api.js             # Axios API calls
│   └── index.css          # Tailwind styles
├── vite.config.js
└── package.json
```

### Backend: LangGraph Agent Workflow
The backend will implement the exact state machine you requested:
1. **Understand Question**: Combine user input with conversation memory and dataset schema.
2. **Analyze Dataset**: Retrieve column types and summary statistics.
3. **Generate Query**: Use the LLM to write Pandas code or SQL.
4. **Execute Query**: Run the code securely on the backend dataframe.
5. **Validate Result**: Check for errors or empty results; retry if necessary.
6. **Generate Chart?**: If the LLM determines a visual is helpful, determine chart type and configuration.
7. **Generate Explanation**: Format the final response, including the data, chart config, and textual answer.

### Frontend: UI/UX Design
- **Dark/Light Mode Premium Aesthetic**: A sleek, modern dashboard UI using Tailwind CSS.
- **Sidebar**: Manage data sources (Upload CSV/Excel or Database Connection).
- **Main Chat Area**: Conversational UI where the user types queries.
- **Rich Message Bubbles**: Responses will dynamically render markdown text, data tables, and Recharts components based on the backend's JSON payload.

## Verification Plan

### Automated/Unit Verification
- Test file upload endpoint with a sample CSV.
- Test LangGraph workflow locally with mock questions to ensure states transition correctly (Question -> Code Gen -> Execution -> Answer).

### Manual Verification
- Start FastAPI backend (`uvicorn backend.main:app --reload`).
- Start Vite frontend (`npm run dev`).
- Upload a sample dataset via the UI.
- Ask questions requiring tabular data (e.g., "Show me the top 5 rows").
- Ask questions requiring charts (e.g., "Show me a bar chart of sales by product").
- Verify that follow-up questions retain context.
- Test the PDF download functionality for query documentation.
