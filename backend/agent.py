import pandas as pd
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
import os
import json
import traceback
from dotenv import load_dotenv
from sqlalchemy import create_engine
import warnings

# Suppress warnings from langchain_google_genai for clean terminal output
warnings.filterwarnings("ignore", module="langchain_google_genai")

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class GraphState(TypedDict):
    question: str
    dataset_path: str
    db_uri: str
    df_info: str
    sql_query: str
    execution_result: Any
    chart_needed: bool
    chart_config: Optional[Dict[str, Any]]
    final_answer: str
    error: str

class QueryGeneration(BaseModel):
    sql_query: str = Field(description="The SQLite query to execute. Do not include markdown formatting. The table name is 'data_table'.")
    chart_needed: bool = Field(description="True if the user's question is best answered with a chart/graph.")

class ChartGeneration(BaseModel):
    type: str = Field(description="The type of chart: 'bar', 'line', 'pie', or 'scatter'")
    xKey: str = Field(description="The column name to use for the X axis")
    yKey: str = Field(description="The column name to use for the Y axis")
    title: str = Field(description="The title of the chart")

def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0
    )

def analyze_dataset_node(state: GraphState):
    try:
        path = state["dataset_path"]
        
        # Create a temporary SQLite database in the same directory as the dataset
        db_path = f"{path}.db"
        db_uri = f"sqlite:///{db_path}"
        engine = create_engine(db_uri)
        
        # Only parse the full CSV and write to SQL if the DB doesn't exist
        if not os.path.exists(db_path):
            if path.endswith('.csv'):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            df.to_sql("data_table", engine, index=False, if_exists="replace")
        
        # Fast extraction of schema and sample data using SQL
        sample_df = pd.read_sql("SELECT * FROM data_table LIMIT 3", engine)
        count_df = pd.read_sql("SELECT COUNT(*) as cnt FROM data_table", engine)
        total_rows = count_df.iloc[0]['cnt']
        
        info = []
        info.append(f"Table name: data_table")
        info.append(f"Columns: {', '.join(sample_df.columns)}")
        info.append(f"Shape: {total_rows} rows, {len(sample_df.columns)} columns")
        info.append("Data Types:\n" + str(sample_df.dtypes))
        info.append("Sample Data (first 3 rows):\n" + sample_df.to_string())
        
        return {"df_info": "\n".join(info), "db_uri": db_uri}
    except Exception as e:
        return {"error": f"Failed to analyze dataset: {str(e)}"}

def generate_query_node(state: GraphState):
    if state.get("error"): return state
    
    llm = get_llm().with_structured_output(QueryGeneration)
    
    system_prompt = (
        "You are an expert SQL analyst. Write a SQLite query to answer the user's question.\n"
        "The data is available in a table named `data_table`.\n"
        "Only generate the SQL query (no markdown block, just the query itself). Ensure the query is valid SQLite."
    )
    
    user_prompt = f"""Dataset Schema Info:
{state.get('df_info', 'No dataset info')}

User Question: {state['question']}"""
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        return {
            "sql_query": response.sql_query,
            "chart_needed": response.chart_needed
        }
    except Exception as e:
        return {"error": f"Failed to generate query: {str(e)}"}

def execute_query_node(state: GraphState):
    if state.get("error"): return state
    
    sql_query = state["sql_query"]
    db_uri = state.get("db_uri")
    
    if not db_uri:
        return {"error": "No database URI found."}
    
    try:
        engine = create_engine(db_uri)
        result = pd.read_sql(sql_query, engine)
        
        if isinstance(result, pd.DataFrame):
            serializable_result = result.to_dict(orient='records')
        elif isinstance(result, pd.Series):
            serializable_result = result.to_frame().to_dict(orient='records')
        else:
            serializable_result = str(result)
            
        return {"execution_result": serializable_result}
    except Exception as e:
        return {"error": f"Execution failed: {traceback.format_exc()}"}

def validate_node(state: GraphState):
    return state

def generate_chart_node(state: GraphState):
    if state.get("error") or not state.get("chart_needed"): 
        return {"chart_config": None}
    
    llm = get_llm().with_structured_output(ChartGeneration)
    
    system_prompt = "The user asked a question that requires a chart. Based on the execution result, suggest the best chart configuration for Recharts."
    user_prompt = f"""User Question: {state['question']}
Execution Result snippet: {str(state.get('execution_result', ''))[:500]}"""
    
    try:
        config = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        return {"chart_config": config.dict()}
    except Exception as e:
        return {"chart_config": None}

def generate_explanation_node(state: GraphState):
    if state.get("error"): 
        return {"final_answer": f"I encountered an error: {state['error']}"}
        
    llm = get_llm()
    system_prompt = "You are a helpful data analyst. Explain the results of the analysis in plain English to the user. Do not mention the python code or Pandas. Just answer their question naturally based on the results."
    user_prompt = f"""User Question: {state['question']}
Analysis Result: {str(state.get('execution_result', ''))[:1000]}"""
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        content = response.content
        if isinstance(content, list):
            text_parts = []
            for part in content:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
                else:
                    text_parts.append(str(part))
            final_text = "\n".join(text_parts)
        else:
            final_text = str(content)
        return {"final_answer": final_text}
    except Exception as e:
        return {"final_answer": "Here are the results of your query."}

workflow = StateGraph(GraphState)

workflow.add_node("analyze", analyze_dataset_node)
workflow.add_node("generate_query", generate_query_node)
workflow.add_node("execute", execute_query_node)
workflow.add_node("validate", validate_node)
workflow.add_node("generate_chart", generate_chart_node)
workflow.add_node("explain", generate_explanation_node)

workflow.add_edge(START, "analyze")
workflow.add_edge("analyze", "generate_query")
workflow.add_edge("generate_query", "execute")
workflow.add_edge("execute", "validate")
workflow.add_edge("validate", "generate_chart")
workflow.add_edge("generate_chart", "explain")
workflow.add_edge("explain", END)

app = workflow.compile()

def process_chat(question: str, dataset_path: str):
    initial_state = {
        "question": question,
        "dataset_path": dataset_path,
        "error": ""
    }
    result = app.invoke(initial_state)
    return result
