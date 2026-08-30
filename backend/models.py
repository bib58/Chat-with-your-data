from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ChatRequest(BaseModel):
    message: str
    session_id: str
    dataset_path: str = ""
    db_uri: str = ""

class ConnectRequest(BaseModel):
    connection_string: str

class ChartConfig(BaseModel):
    type: str
    xKey: str
    yKey: str
    title: str

class ChatResponse(BaseModel):
    answer: str
    table_data: Optional[List[Dict[str, Any]]] = None
    chart_config: Optional[ChartConfig] = None
    query_executed: Optional[str] = None

class CleanupRequest(BaseModel):
    dataset_path: str
