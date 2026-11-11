from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
try:
    from .models import (
        ChatRequest,
        ChatResponse,
        ChartConfig,
        ConnectRequest,
        CleanupRequest,
        FeedbackRequest,
    )
    from .agent import process_chat
    from .feedback_store import initialize_feedback_database, save_feedback, submit_langsmith_feedback
except ImportError:
    from models import (
        ChatRequest,
        ChatResponse,
        ChartConfig,
        ConnectRequest,
        CleanupRequest,
        FeedbackRequest,
    )
    from agent import process_chat
    from feedback_store import initialize_feedback_database, save_feedback, submit_langsmith_feedback

app = FastAPI()

configured_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:4173,https://data-chit-chat.vercel.app",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
initialize_feedback_database()

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = os.path.basename(file.filename or "")
    if not filename.lower().endswith((".csv", ".xlsx", ".json")):
        raise HTTPException(status_code=400, detail="Only CSV, Excel, or JSON files are allowed.")
    
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"dataset_path": file_path, "filename": filename}


@app.post("/cleanup")
async def cleanup_files(request: CleanupRequest):
    path = request.dataset_path
    try:
        is_upload = os.path.commonpath(
            [os.path.abspath(path), os.path.abspath(UPLOAD_DIR)]
        ) == os.path.abspath(UPLOAD_DIR)
    except ValueError:
        is_upload = False
    if path and is_upload and os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass
        db_path = f"{path}.db"
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass
    return {"status": "ok"}

@app.post("/connect")
async def connect_database(request: ConnectRequest):
    """Connect to a SQL Server database using a connection string."""
    from sqlalchemy import create_engine, inspect
    import pandas as pd
    
    connection_string = request.connection_string.strip()
    
    if not connection_string:
        raise HTTPException(status_code=400, detail="Connection string is required.")
    try:
        engine = create_engine(connection_string)
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            raise HTTPException(status_code=400, detail="No tables found in the database.")
        
        tables_info = []
        for table_name in tables:
            try:
                sample_df = pd.read_sql(f"SELECT TOP 3 * FROM [{table_name}]", engine)
                count_df = pd.read_sql(f"SELECT COUNT(*) as cnt FROM [{table_name}]", engine)
                total_rows = count_df.iloc[0]["cnt"]
                
                info = (
                    f"Table: {table_name}\n"
                    f"  Columns: {', '.join(sample_df.columns)}\n"
                    f"  Rows: {total_rows}\n"
                    f"  Types: {dict(sample_df.dtypes)}\n"
                    f"  Sample: {sample_df.head(2).to_string()}"
                )
                tables_info.append(info)
            except Exception:
                tables_info.append(f"Table: {table_name} (could not read schema)")
        
        db_name = "SQL Server DB"
        try:
            if "/" in connection_string:
                db_name = connection_string.rstrip("/").split("/")[-1].split("?")[0]
        except Exception:
            pass
        
        engine.dispose()
        
        return {
            "db_uri": connection_string,
            "filename": f"{db_name}",
            "tables_info": "\n\n".join(tables_info),
            "tables": tables,
            "dataset_path": ""
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    request_id = request.request_id or str(uuid.uuid4())
    if request.db_uri:
        result = process_chat(
            request.message,
            dataset_path="",
            db_uri=request.db_uri,
            model_name=request.model_name,
            request_id=request_id,
            session_id=request.session_id,
            langsmith_extra={
                "metadata": {
                    "request_id": request_id,
                    "session_id": request.session_id,
                    "execution_mode": "sql_server",
                    "task_type": "text_to_sql",
                },
                "tags": ["chat", "sql_server", "text-to-sql"],
            },
        )
    elif request.dataset_path and os.path.exists(request.dataset_path):
        result = process_chat(
            request.message,
            dataset_path=request.dataset_path,
            model_name=request.model_name,
            request_id=request_id,
            session_id=request.session_id,
            langsmith_extra={
                "metadata": {
                    "request_id": request_id,
                    "session_id": request.session_id,
                    "execution_mode": "file_upload",
                    "task_type": "text_to_sql",
                },
                "tags": ["chat", "file_upload", "text-to-sql"],
            },
        )
    else:
        raise HTTPException(status_code=400, detail="No data source provided. Upload a file or connect to SQL Server.")
        
    if result.get("error"):
        error_msg = result.get("final_answer") or f"Error: {result['error']}"
        return ChatResponse(
            answer=error_msg,
            message_id=request_id,
            trace_id=result.get("trace_id"),
            table_data=None,
            chart_config=None,
            query_executed=result.get("sql_query"),
            tags=result.get("tags"),
            token_financials=result.get("token_financials"),
            reasoning_content=result.get("reasoning_content")
        )

    if result.get("off_topic"):
        raw_answer = result.get("final_answer", "I'm a data analysis assistant — I can only answer questions about your uploaded dataset.")
        answer_str = str(raw_answer) if not isinstance(raw_answer, list) else "\n".join(
            part.get("text", str(part)) if isinstance(part, dict) else str(part) for part in raw_answer
        )
        return ChatResponse(
            answer=answer_str,
            message_id=request_id,
            trace_id=result.get("trace_id"),
            table_data=None,
            chart_config=None,
            query_executed=None,
            tags=result.get("tags"),
            token_financials=result.get("token_financials"),
            reasoning_content=result.get("reasoning_content")
        )

    execution_result = result.get("execution_result")
    table_data = None
    if isinstance(execution_result, list):
        table_data = execution_result
        
    chart_cfg = None
    if result.get("chart_config"):
        cfg = result["chart_config"]
        chart_cfg = ChartConfig(
            type=cfg.get("type", "bar"),
            xKey=cfg.get("xKey", ""),
            yKey=cfg.get("yKey", ""),
            title=cfg.get("title", "")
        )
        
    raw_answer = result.get("final_answer", "No answer generated.")
    if isinstance(raw_answer, list):
        answer_str = "\n".join(
            part.get("text", str(part)) if isinstance(part, dict) else str(part)
            for part in raw_answer
        )
    else:
        answer_str = str(raw_answer)

    return ChatResponse(
        answer=answer_str,
        message_id=request_id,
        trace_id=result.get("trace_id"),
        table_data=table_data,
        chart_config=chart_cfg,
        query_executed=result.get("sql_query"),
        tags=result.get("tags"),
        token_financials=result.get("token_financials"),
        reasoning_content=result.get("reasoning_content")
    )


@app.post("/feedback")
async def feedback(request: FeedbackRequest):
    if not request.message_id.strip():
        raise HTTPException(status_code=422, detail="message_id is required.")

    try:
        saved = save_feedback(
            message_id=request.message_id.strip(),
            trace_id=request.trace_id,
            rating=request.rating,
            query=request.query,
            response=request.response,
            reason=request.reason,
            comment=request.comment,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to save feedback.") from exc

    submit_langsmith_feedback(request.trace_id, request.rating, request.reason, request.comment)
    return {
        "status": "saved",
        "message_id": saved.message_id,
        "rating": saved.rating,
    }
