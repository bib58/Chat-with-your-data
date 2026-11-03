"""
First test (ChatOpenRouter version): send ONE question to ONE model via OpenRouter
Setup:
  pip install langchain-openrouter
"""

from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()
MODEL="openai/gpt-4o" 

with open("schema.sql", encoding="utf-8") as f:
    schema = f.read().strip()

question = "Who scored the most runs in 2024?"

system_msg = (
    "You are a text-to-SQL generator. "
    "Given a database schema and a question, return a single SQL query that answers it. "
    "Use SQLite syntax. Return only the SQL query."
)
user_msg = f"Schema:\n{schema}\n\nQuestion: {question}\n\nSQL:"

llm = ChatOpenRouter(
    model=MODEL,
    temperature=0,
    max_tokens=300
)

messages = [
    SystemMessage(content=system_msg),
    HumanMessage(content=user_msg),
]
response = llm.invoke(messages)

raw_sql = response.content

print("=" * 60)
print("QUESTION:", question)
print("=" * 60)
print("RAW MODEL OUTPUT:")
print(raw_sql)
print("=" * 60)
