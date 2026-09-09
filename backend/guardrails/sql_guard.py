import re
from typing import Tuple, Optional, List
import sqlglot
import sqlglot.expressions as exp

# Forbidden DDL / DML operations and destructive verbs
FORBIDDEN_KEYWORDS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bREPLACE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bMERGE\b",
    r"\bEXEC(UTE)?\b",
]

# High-risk system procedures and dangerous functions
DANGEROUS_SYSTEM_PATTERNS = [
    r"\bxp_cmdshell\b",
    r"\bsp_executesql\b",
    r"\bsp_configure\b",
    r"\bopenrowset\b",
    r"\bopendatasource\b",
    r"\bload_extension\b",
    r"\battach\s+database\b",
    r"\bshutdown\b",
]

DISALLOWED_AST_TYPES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.Command,
    exp.Merge,
    exp.TruncateTable,
)

DEFAULT_ROW_LIMIT = 50


def clean_sql_string(raw_sql: str) -> str:
    """Strips markdown code fences, comments, and extra whitespaces."""
    if not raw_sql:
        return ""
    sql = raw_sql.strip()
    if sql.startswith("```"):
        lines = sql.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        sql = "\n".join(lines).strip()
    return sql


def validate_sql(
    query: str,
    dialect: str = "sqlite",
    allowed_tables: Optional[List[str]] = None,
) -> Tuple[bool, str, Optional[str]]:
    """
    Validates that a SQL query is strictly read-only, single-statement,
    targets valid tables, and does not contain dangerous commands.

    Args:
        query: The raw SQL query string.
        dialect: 'sqlite' or 'tsql'.
        allowed_tables: Optional list of authorized table names.

    Returns:
        (is_safe, validated_query, error_message)
    """
    clean_query = clean_sql_string(query)
    if not clean_query:
        return False, "", "SQL query is empty."

    # 1. Fast keyword rejection for mutating verbs
    for pattern in FORBIDDEN_KEYWORDS:
        if re.search(pattern, clean_query, re.IGNORECASE):
            match = re.search(pattern, clean_query, re.IGNORECASE).group()
            return False, clean_query, (
                f"SQL Guardrail Violation: Mutating operation '{match.upper()}' is not permitted. "
                "Only read-only SELECT queries are allowed."
            )

    # 2. Check for dangerous system calls / procedures
    for pattern in DANGEROUS_SYSTEM_PATTERNS:
        if re.search(pattern, clean_query, re.IGNORECASE):
            return False, clean_query, (
                "SQL Guardrail Violation: Dangerous system procedure or function detected."
            )

    # 3. AST Parsing with sqlglot
    read_dialect = "tsql" if dialect.lower() in ("tsql", "mssql", "sqlserver") else "sqlite"
    try:
        parsed_statements = [stmt for stmt in sqlglot.parse(clean_query, read=read_dialect) if stmt]
    except Exception as e:
        try:
            parsed_statements = [stmt for stmt in sqlglot.parse(clean_query) if stmt]
        except Exception as e2:
            return False, clean_query, f"SQL Guardrail Violation: Invalid SQL syntax ({str(e2)})."

    # 4. Enforce single statement execution
    if len(parsed_statements) == 0:
        return False, clean_query, "SQL Guardrail Violation: No executable SQL statement found."
    if len(parsed_statements) > 1:
        return False, clean_query, (
            "SQL Guardrail Violation: Multi-statement execution (query chaining) is prohibited."
        )

    stmt = parsed_statements[0]

    # 5. AST Read-only check: Must be a Select or Union
    if not isinstance(stmt, (exp.Select, exp.Union)):
        if not stmt.find(exp.Select):
            return False, clean_query, (
                "SQL Guardrail Violation: Only SELECT queries are permitted."
            )

    for disallowed_type in DISALLOWED_AST_TYPES:
        if stmt.find(disallowed_type):
            return False, clean_query, (
                f"SQL Guardrail Violation: Prohibited statement structure detected ({disallowed_type.__name__})."
            )

    # 6. Validate Table Names (if allowed_tables provided)
    if allowed_tables:
        normalized_allowed = {t.lower().strip("[]`\"") for t in allowed_tables}
        cte_names = set()
        with_clause = stmt.args.get("with")
        if with_clause:
            for cte in with_clause.expressions:
                if cte.alias:
                    cte_names.add(cte.alias.lower().strip("[]`\""))

        for table_node in stmt.find_all(exp.Table):
            table_name = table_node.name.lower().strip("[]`\"")
            if table_name and table_name not in normalized_allowed and table_name not in cte_names:
                return False, clean_query, (
                    f"SQL Guardrail Violation: Access to table '{table_node.name}' is unauthorized. "
                    f"Allowed tables: {', '.join(allowed_tables)}."
                )

    # 7. Bound queries with limit if missing
    validated_query = clean_query
    if read_dialect == "sqlite":
        if not stmt.args.get("limit") and not re.search(r"\bLIMIT\s+\d+\b", clean_query, re.IGNORECASE):
            validated_query = f"{clean_query.rstrip(';')} LIMIT {DEFAULT_ROW_LIMIT}"
    elif read_dialect == "tsql":
        if not stmt.args.get("limit") and not re.search(r"\bTOP\s+\d+\b", clean_query, re.IGNORECASE):
            if re.match(r"^\s*SELECT\b", clean_query, re.IGNORECASE):
                validated_query = re.sub(
                    r"^\s*SELECT\b",
                    f"SELECT TOP {DEFAULT_ROW_LIMIT}",
                    clean_query,
                    count=1,
                    flags=re.IGNORECASE,
                )

    return True, validated_query, None
