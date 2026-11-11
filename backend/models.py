from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Literal

class ChatRequest(BaseModel):
    message: str
    session_id: str
    dataset_path: str = ""
    db_uri: str = ""
    use_reasoning: bool = False
    model_name: Optional[str] = None
    request_id: Optional[str] = None

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
    estimated_cost_usd: Optional[float] = None
    model_name: str = ""

class ChatResponse(BaseModel):
    answer: str
    message_id: str
    trace_id: Optional[str] = None
    table_data: Optional[List[Dict[str, Any]]] = None
    chart_config: Optional[ChartConfig] = None
    query_executed: Optional[str] = None
    tags: Optional[List[str]] = None
    token_financials: Optional[TokenFinancials] = None
    reasoning_content: Optional[str] = None

class CleanupRequest(BaseModel):
    dataset_path: str


class FeedbackRequest(BaseModel):
    message_id: str = Field(min_length=1, max_length=255)
    trace_id: Optional[str] = None
    rating: Literal[1, -1]
    query: Optional[str] = None
    response: Optional[str] = None
    reason: Optional[str] = None
    comment: Optional[str] = None
