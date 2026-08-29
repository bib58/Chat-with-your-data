import pandas as pd
from typing import TypedDict, Any, Optional, Dict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import os
import time

# Suppress warnings from langchain_google_genai for clean terminal output
warnings.filterwarnings("ignore", module="langchain_google_genai")

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# ============================================================
# OPTIMIZATION 1: Singleton LLM — created once, reused forever
# ============================================================
_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# OPTIMIZATION 4: Default to gemini-3.6-flash (much faster for SQL)
_model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

LLM = ChatGoogleGenerativeAI(
    model=_model_name,
    google_api_key=_api_key,
    temperature=0,
)

# ============================================================
# OPTIMIZATION 2: Schema cache — skip re-analysis on every query
# ============================================================
_schema_cache: Dict[str, Dict[str, str]] = {}


# ---------- State ----------
class GraphState(TypedDict):
    question: str
    dataset_path: str
    db_uri: str
    df_info: str
    sql_query: str
    sql_dialect: str          # "sqlite" or "tsql"
    execution_result: Any
    chart_needed: bool
    chart_config: Optional[Dict[str, Any]]
    final_answer: str
    error: str


# ============================================================
# OPTIMIZATION 3: Single structured output model
#   Combines SQL generation + chart decision + answer into ONE
#   LLM call instead of two separate calls.
# ============================================================
class QueryAndAnswer(BaseModel):
    sql_query: str = Field(
        description=(
            "The SQLite query to answer the user's question. "
            "No markdown formatting. The table name is 'data_table'."
        )
    )
    chart_needed: bool = Field(
        description="True if a chart/graph would help visualize the answer."
    )
    answer_sketch: str = Field(
        description=(
            "A brief 1-3 sentence natural-language answer describing what "
            "the query reveals. The raw data table will be shown separately, "
            "so don't list every row — just give the key insight."
        )
    )


# ==================== GRAPH NODES ====================

def analyze_dataset_node(state: GraphState):
    """Analyze dataset with caching — supports both CSV→SQLite and SQL Server."""
    start = time.perf_counter()
    
    db_uri = state.get("db_uri", "")
    path = state.get("dataset_path", "")
    
    # Determine cache key
    cache_key = db_uri if db_uri else path
    
    # ---- Cache hit → instant return ----
    if cache_key and cache_key in _schema_cache:
        cached = _schema_cache[cache_key]
        elapsed = time.perf_counter() - start
        print(f"⚡ ANALYZE (cached): {elapsed:.4f}s")
        return {
            "df_info": cached["df_info"],
            "db_uri": cached["db_uri"],
            "sql_dialect": cached["sql_dialect"],
        }

    try:
        # ---- SQL Server connection (link provided) ----
        if db_uri:
            engine = create_engine(db_uri)
            sql_dialect = "tsql"
            
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            info_parts = []
            for table_name in tables:
                try:
                    sample_df = pd.read_sql(f"SELECT TOP 3 * FROM [{table_name}]", engine)
                    count_df = pd.read_sql(f"SELECT COUNT(*) as cnt FROM [{table_name}]", engine)
                    total_rows = count_df.iloc[0]["cnt"]
                    
                    info_parts.append(
                        f"Table: {table_name}\n"
                        f"  Columns: {', '.join(sample_df.columns)}\n"
                        f"  Shape: {total_rows} rows, {len(sample_df.columns)} columns\n"
                        f"  Data Types:\n{sample_df.dtypes}\n"
                        f"  Sample Data:\n{sample_df.to_string()}"
                    )
                except Exception as e:
                    info_parts.append(f"Table: {table_name} (error reading: {e})")
            
            df_info = "\n\n".join(info_parts)
            engine.dispose()
        
        # ---- CSV/Excel upload → SQLite (existing behavior) ----
        else:
            sql_dialect = "sqlite"
            db_path = f"{path}.db"
            db_uri = f"sqlite:///{db_path}"
            engine = create_engine(db_uri)

            if not os.path.exists(db_path):
                print("⚡ Creating SQLite database...")
                if path.endswith('.csv'):
                    df = pd.read_csv(path)
                else:
                    df = pd.read_excel(path)
                df.to_sql("data_table", engine, index=False, if_exists="replace")

            sample_df = pd.read_sql("SELECT * FROM data_table LIMIT 3", engine)
            count_df = pd.read_sql(
                "SELECT COUNT(*) as cnt FROM data_table", engine
            )
            total_rows = count_df.iloc[0]["cnt"]

            df_info = "\n".join([
                "Table name: data_table",
                f"Columns: {', '.join(sample_df.columns)}",
                f"Shape: {total_rows} rows, {len(sample_df.columns)} columns",
                f"Data Types:\n{sample_df.dtypes}",
                f"Sample Data:\n{sample_df.to_string()}",
            ])

        # Store in cache
        _schema_cache[cache_key] = {
            "df_info": df_info,
            "db_uri": db_uri,
            "sql_dialect": sql_dialect,
        }

        elapsed = time.perf_counter() - start
        print(f"⏱️ ANALYZE: {elapsed:.2f}s")
        return {"df_info": df_info, "db_uri": db_uri, "sql_dialect": sql_dialect}

    except Exception as e:
        print(f"❌ ANALYZE: {time.perf_counter() - start:.2f}s")
        return {"error": f"Failed to analyze dataset: {str(e)}"}


def generate_query_and_answer_node(state: GraphState):
    """Single LLM call → SQL + chart decision + answer sketch."""
    if state.get("error"):
        return state

    start = time.perf_counter()

    llm_structured = LLM.with_structured_output(QueryAndAnswer)

    sql_dialect = state.get("sql_dialect", "sqlite")
    
    if sql_dialect == "tsql":
        dialect_instructions = (
            "1. Write a T-SQL (SQL Server) query to answer it. Use the correct table names from the schema.\n"
            "Rules:\n"
            "- Only valid T-SQL / SQL Server syntax.\n"
            "- Use TOP instead of LIMIT (e.g., SELECT TOP 50 ...).\n"
            "- Use square brackets for table/column names with spaces: [table name].\n"
            "- No markdown formatting in the SQL.\n"
            "- TOP 50 rows max unless the user asks for everything."
        )
    else:
        dialect_instructions = (
            "1. Write a SQLite query to answer it (table: `data_table`).\n"
            "Rules:\n"
            "- Only valid SQLite syntax.\n"
            "- No markdown formatting in the SQL.\n"
            "- LIMIT results to 50 rows max unless the user asks for everything."
        )

    system_prompt = (
        "You are an expert SQL data analyst. Given a dataset schema and a "
        "user question:\n"
        f"{dialect_instructions}\n"
        "2. Decide if a chart would help visualize the answer.\n"
        "3. Write a brief natural-language answer (1-3 sentences) summarising "
        "what the query reveals. The raw data will be shown in a table, so "
        "don't list every row — just state the insight."
    )

    user_prompt = (
        f"Dataset Schema:\n{state.get('df_info', 'N/A')}\n\n"
        f"Question: {state['question']}"
    )

    try:
        response = llm_structured.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])

        elapsed = time.perf_counter() - start
        print(f"⏱️ LLM (single call): {elapsed:.2f}s")
        print(f"📝 SQL ({sql_dialect}): {response.sql_query}")
        print(f"📊 Chart: {response.chart_needed}")

        return {
            "sql_query": response.sql_query,
            "chart_needed": response.chart_needed,
            "final_answer": response.answer_sketch,
        }

    except Exception as e:
        print(f"❌ LLM: {time.perf_counter() - start:.2f}s")
        return {"error": f"Failed to generate query: {str(e)}"}


def execute_query_node(state: GraphState):
    """Execute the generated SQL against the cached SQLite database."""
    if state.get("error"):
        return state

    start = time.perf_counter()
    db_uri = state.get("db_uri")

    if not db_uri:
        return {"error": "No database URI found."}

    try:
        engine = create_engine(db_uri)
        result = pd.read_sql(state["sql_query"], engine)

        if isinstance(result, pd.DataFrame):
            serializable = result.to_dict(orient="records")
        elif isinstance(result, pd.Series):
            serializable = result.to_frame().to_dict(orient="records")
        else:
            serializable = str(result)

        elapsed = time.perf_counter() - start
        print(f"⏱️ SQL EXEC: {elapsed:.2f}s")
        return {"execution_result": serializable}

    except Exception as e:
        print(f"❌ SQL EXEC: {time.perf_counter() - start:.2f}s")
        traceback.print_exc()
        return {"error": f"Execution failed: {str(e)}"}


def format_response_node(state: GraphState):
    """Build chart config heuristically and enrich the answer — NO LLM call."""
    if state.get("error"):
        return {
            "final_answer": f"I encountered an error: {state['error']}",
            "chart_config": None,
        }

    start = time.perf_counter()

    result = state.get("execution_result", [])
    answer = state.get("final_answer", "Here are the results of your query.")

    # --- Enrich answer for scalar results (COUNT, SUM, AVG, etc.) ---
    if isinstance(result, list) and len(result) == 1 and len(result[0]) == 1:
        key = list(result[0].keys())[0]
        value = result[0][key]
        answer = f"{answer}\n\n**{key}:** {value}"

    # --- Chart config (heuristic — no LLM call) ---
    chart_config = None
    if state.get("chart_needed"):
        if result and isinstance(result, list) and len(result) > 0:
            columns = list(result[0].keys())
            if len(columns) >= 2:
                x_key = columns[0]
                y_key = columns[1]
                # Use line chart for many data points (time-series feel)
                chart_type = "line" if len(result) > 12 else "bar"
                chart_config = {
                    "type": chart_type,
                    "xKey": x_key,
                    "yKey": y_key,
                    "title": f"{y_key} by {x_key}",
                }

    elapsed = time.perf_counter() - start
    print(f"⏱️ FORMAT: {elapsed:.4f}s")

    return {"final_answer": answer, "chart_config": chart_config}


# ============================================================
# Optimised graph: 4 nodes, 1 LLM call, 0 no-ops
#
#   START → analyze → generate → execute → format → END
# ============================================================
workflow = StateGraph(GraphState)

workflow.add_node("analyze", analyze_dataset_node)
workflow.add_node("generate", generate_query_and_answer_node)
workflow.add_node("execute", execute_query_node)
workflow.add_node("format", format_response_node)

workflow.add_edge(START, "analyze")
workflow.add_edge("analyze", "generate")
workflow.add_edge("generate", "execute")
workflow.add_edge("execute", "format")
workflow.add_edge("format", END)

app = workflow.compile()


def process_chat(question: str, dataset_path: str = "", db_uri: str = ""):
    initial_state = {
        "question": question,
        "dataset_path": dataset_path,
        "db_uri": db_uri,
        "error": "",
    }
    result = app.invoke(initial_state)
    return result
