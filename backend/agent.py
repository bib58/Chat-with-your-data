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

# Load .env from current directory and backend directory
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class GraphState(TypedDict):
    question: str
    dataset_path: str
    df_info: str
    pandas_code: str
    execution_result: Any
    chart_needed: bool
    chart_config: Optional[Dict[str, Any]]
    final_answer: str
    error: str

class QueryGeneration(BaseModel):
    pandas_code: str = Field(description="The pandas code to execute. The dataframe is available as 'df'. Assign the final result to a variable named 'result'.")
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
        if path.endswith('.csv'):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
        
        info = []
        info.append(f"Columns: {', '.join(df.columns)}")
        info.append(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
        info.append("Data Types:\n" + str(df.dtypes))
        info.append("Sample Data (first 3 rows):\n" + df.head(3).to_string())
        
        return {"df_info": "\n".join(info)}
    except Exception as e:
        return {"error": f"Failed to analyze dataset: {str(e)}"}

def generate_query_node(state: GraphState):
    if state.get("error"): return state
    
    llm = get_llm().with_structured_output(QueryGeneration)
    
    system_prompt = (
        "You are a Python Pandas expert. Write pandas code to answer the user's question.\n"
        "The dataframe is already loaded as a variable named `df`.\n"
        "You must assign the final output to a variable named `result`.\n"
        "If the result is a dataframe, ensure it contains the necessary columns."
    )
    
    user_prompt = f"""Dataset Info:
{state.get('df_info', 'No dataset info')}

User Question: {state['question']}"""
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        return {
            "pandas_code": response.pandas_code,
            "chart_needed": response.chart_needed
        }
    except Exception as e:
        return {"error": f"Failed to generate query: {str(e)}"}

def execute_query_node(state: GraphState):
    if state.get("error"): return state
    
    code = state["pandas_code"]
    path = state["dataset_path"]
    
    try:
        if path.endswith('.csv'):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)
            
        local_vars = {"df": df, "pd": pd}
        
        exec(code, {}, local_vars)
        
        result = local_vars.get("result", "No 'result' variable was assigned in the code.")
        
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
