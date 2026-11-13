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
    question: str = Field(min_length=1, max_length=10000)
    answer: str = Field(min_length=1, max_length=100000)
    session_id: Optional[str] = Field(default=None, max_length=255)
    message_id: str = Field(min_length=1, max_length=255)
    feedback_type: Literal["upvote", "downvote"]
    feedback_reason: Optional[str] = Field(default=None, max_length=2000)
