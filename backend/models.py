from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class ChatRequest(BaseModel):
    message: str
    session_id: str
    dataset_path: str = ""
    db_uri: str = ""
    use_reasoning: bool = False
    model_name: Optional[str] = None

class ConnectRequest(BaseModel):
    connection_string: str

class ChartConfig(BaseModel):
    type: str
    xKey: str
    yKey: str
    title: str

class TokenFinancials(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    model_name: str = ""

class ChatResponse(BaseModel):
    answer: str
    table_data: Optional[List[Dict[str, Any]]] = None
    chart_config: Optional[ChartConfig] = None
    query_executed: Optional[str] = None
    tags: Optional[List[str]] = None
    token_financials: Optional[TokenFinancials] = None
    reasoning_content: Optional[str] = None

class CleanupRequest(BaseModel):
    dataset_path: str
