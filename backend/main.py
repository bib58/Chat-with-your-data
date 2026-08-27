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
    from .models import ChatRequest, ChatResponse, ChartConfig
    from .agent import process_chat
except ImportError:
    from models import ChatRequest, ChatResponse, ChartConfig
    from agent import process_chat

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed.")
    
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"dataset_path": file_path, "filename": file.filename}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.dataset_path or not os.path.exists(request.dataset_path):
        raise HTTPException(status_code=400, detail="Invalid or missing dataset path.")
        
    result = process_chat(request.message, request.dataset_path)
    
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
        query_executed=result.get("pandas_code")
    )
