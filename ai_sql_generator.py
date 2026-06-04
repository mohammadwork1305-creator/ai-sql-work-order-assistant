import os
import re
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_PATH = "Test1.db"

DATABASE_SCHEMA = """
Tables:

Boroughs(
    BoroughID INTEGER PRIMARY KEY,
    BoroughName TEXT
)

Developments(
    DevelopmentID INTEGER PRIMARY KEY,
    DevelopmentName TEXT,
    BoroughID INTEGER,
    FOREIGN KEY (BoroughID) REFERENCES Boroughs(BoroughID)
)

Vendors(
    VendorID INTEGER PRIMARY KEY,
    VendorName TEXT
)

Statuses(
    StatusID INTEGER PRIMARY KEY,
    StatusName TEXT
)

WorkOrders(
    WorkOrderID INTEGER PRIMARY KEY,
    DevelopmentID INTEGER,
    VendorID INTEGER,
    StatusID INTEGER,
    CreatedDate DATE,
    ScheduledDate DATE,
    CompletedDate DATE,
    WorkType TEXT,
    FOREIGN KEY (DevelopmentID) REFERENCES Developments(DevelopmentID),
    FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID),
    FOREIGN KEY (StatusID) REFERENCES Statuses(StatusID)
)

Invoices(
    InvoiceID INTEGER PRIMARY KEY,
    WorkOrderID INTEGER,
    InvoiceAmount DECIMAL(10,2),
    FundingSource TEXT,
    InvoiceDate DATE,
    FOREIGN KEY (WorkOrderID) REFERENCES WorkOrders(WorkOrderID)
)
"""

def generate_sql(user_question):
    system_prompt = f"""
You are a SQL assistant for a SQLite database.

Rules:
- Generate only one SQL query.
- Use SQLite syntax.
- Only generate SELECT queries.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or REPLACE.
- Do not explain the query.
- Do not use markdown.
- Use full table names, not aliases.
- Add LIMIT 50 unless the question asks for count, sum, average, grouping, or top results.

Database schema:
{DATABASE_SCHEMA}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()
    return sql


def is_safe_select_query(sql):
    sql_clean = sql.strip()
    sql_upper = sql_clean.upper()

    # Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False

    # Block dangerous SQL commands as full words only
    blocked_patterns = [
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bDROP\b",
        r"\bALTER\b",
        r"\bCREATE\b",
        r"\bTRUNCATE\b",
        r"\bREPLACE\b"
    ]

    for pattern in blocked_patterns:
        if re.search(pattern, sql_upper):
            return False

    return True


def run_sql(sql):
    connection = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(sql, connection)
    connection.close()
    return df


if __name__ == "__main__":
    question = input("Ask your database a question: ")

    sql_query = generate_sql(question)

    print("\nGenerated SQL:")
    print(sql_query)

    if is_safe_select_query(sql_query):
        result = run_sql(sql_query)
        print("\nResult:")
        print(result)
    else:
        print("Unsafe SQL detected. Query was not executed.")