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
    from .models import ChatRequest, ChatResponse, ChartConfig, ConnectRequest, CleanupRequest
    from .agent import process_chat
except ImportError:
    from models import ChatRequest, ChatResponse, ChartConfig, ConnectRequest, CleanupRequest
    from agent import process_chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed.")
    
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"dataset_path": file_path, "filename": file.filename}

@app.post("/cleanup")
async def cleanup_files(request: CleanupRequest):
    path = request.dataset_path
    if path and os.path.exists(path) and "uploads" in path:
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
        
        # Test connection and get all table names
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            raise HTTPException(status_code=400, detail="No tables found in the database.")
        
        # Build schema info for all tables
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
        
        # Extract database name from connection string for display
        db_name = "SQL Server DB"
        try:
            # Try to extract db name from the URI
            if "/" in connection_string:
                db_name = connection_string.rstrip("/").split("/")[-1].split("?")[0]
        except Exception:
            pass
        
        engine.dispose()
        
        return {
            "db_uri": connection_string,
            "filename": f"🔗 {db_name}",
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
    # Determine data source: CSV upload or SQL Server link
    if request.db_uri:
        # SQL Server connection
        result = process_chat(request.message, dataset_path="", db_uri=request.db_uri)
    elif request.dataset_path and os.path.exists(request.dataset_path):
        # CSV/Excel upload
        result = process_chat(request.message, dataset_path=request.dataset_path)
    else:
        raise HTTPException(status_code=400, detail="No data source provided. Upload a file or connect to SQL Server.")
        
    if result.get("error"):
        return ChatResponse(answer=f"Error: {result['error']}", table_data=None, chart_config=None, query_executed=None)
        
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
        table_data=table_data,
        chart_config=chart_cfg,
        query_executed=result.get("sql_query")
    )
