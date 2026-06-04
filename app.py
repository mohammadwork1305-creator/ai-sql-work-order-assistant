import os
import re
import sqlite3
import pandas as pd
import streamlit as st
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
- If the user says completed, closed, close, or finished work, treat it as Statuses.StatusName = 'Completed'.
- If the user says open work, treat it as Statuses.StatusName IN ('Pending', 'Scheduled').
- If the user asks for a year, use strftime('%Y', date_column) = 'YYYY'.
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

    return response.choices[0].message.content.strip()


def is_safe_select_query(sql):
    sql_clean = sql.strip()
    sql_upper = sql_clean.upper()

    if not sql_upper.startswith("SELECT"):
        return False

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


def get_database_counts():
    connection = sqlite3.connect(DB_PATH)

    counts = {}

    tables = ["Boroughs", "Developments", "Vendors", "Statuses", "WorkOrders", "Invoices"]

    for table in tables:
        query = f"SELECT COUNT(*) AS TotalRows FROM {table}"
        counts[table] = pd.read_sql_query(query, connection)["TotalRows"][0]

    connection.close()
    return counts


st.set_page_config(
    page_title="AI SQL Work Order Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI-Powered SQL Assistant for Work Order Analytics")

st.markdown(
    """
    This project converts plain English business questions into SQL, runs the query against a 
    synthetic SQLite work order database, and returns analytical results.

    **Tech Stack:** Python · SQLite · SQL · Groq AI · Llama 3.3 · Streamlit · Pandas
    """
)

with st.sidebar:
    st.header("Project Overview")

    st.write(
        """
        This app uses synthetic work order data to demonstrate:
        - Relational database design
        - SQL joins
        - Natural language to SQL
        - AI-powered reporting
        - Business analytics dashboarding
        """
    )

    st.header("Database Tables")

    db_counts = get_database_counts()

    for table, count in db_counts.items():
        st.metric(label=table, value=f"{count:,}")

    st.header("Safety Rule")
    st.write("Only SELECT queries are allowed. Insert, update, delete, drop, and alter commands are blocked.")

sample_questions = [
    "Show pending work orders by borough and development",
    "Show all completed work orders in Manhattan borough in 2026",
    "Show all completed work orders in Brooklyn borough",
    "Which vendor has the highest total invoice amount?",
    "Show total invoice amount by funding source",
    "Count work orders by status",
    "Show completed work orders by vendor",
    "Which borough has the most pending work orders?",
    "Show average invoice amount by vendor",
    "Show monthly work order count in 2026"
]

st.subheader("Ask a Business Question")

selected_question = st.selectbox(
    "Choose a sample question:",
    [""] + sample_questions
)

user_question = st.text_input(
    "Or type your own question:",
    value=selected_question,
    placeholder="Example: Show total invoice amount by borough"
)

run_button = st.button("Generate SQL and Run Query", type="primary")

if run_button:
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Generating SQL and querying database..."):
            try:
                sql_query = generate_sql(user_question)

                st.subheader("Generated SQL")
                st.code(sql_query, language="sql")

                if is_safe_select_query(sql_query):
                    result = run_sql(sql_query)

                    st.subheader("Query Result")

                    col1, col2 = st.columns(2)
                    col1.metric("Rows Returned", len(result))
                    col2.metric("Columns Returned", len(result.columns))

                    st.dataframe(result, use_container_width=True)

                    numeric_columns = result.select_dtypes(include=["number"]).columns.tolist()

                    if len(result) > 0 and numeric_columns:
                        st.subheader("Basic Chart")

                        chart_column = numeric_columns[-1]
                        label_column = result.columns[0]

                        chart_data = result[[label_column, chart_column]].set_index(label_column)
                        st.bar_chart(chart_data)

                    if len(result) == 0:
                        st.info("The query ran successfully, but no records matched the question.")

                else:
                    st.error("Unsafe SQL detected. Query was not executed.")

            except Exception as error:
                st.error(f"Error: {error}")

st.divider()

st.markdown(
    """
    ### Portfolio Summary

    **Project Name:** AI-Powered SQL Assistant for Work Order Analytics  
    **Dataset:** Synthetic work order, vendor, invoice, borough, and development data  
    **Purpose:** Demonstrates how AI can help business users query relational databases without manually writing SQL.
    """
)