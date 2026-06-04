# AI-Powered SQL Assistant for Work Order Analytics

## Project Overview

This project is an AI-powered SQL analytics assistant built with Python, SQLite, Groq AI, Llama 3.3, Streamlit, and Pandas.

The application allows users to ask business questions in plain English. The AI model converts the question into a SQL query, runs it against a synthetic relational work order database, and displays the results in a table and chart.

This project demonstrates relational database design, SQL joins, natural language to SQL generation, business reporting, and dashboard development.

## Important Note

This project uses fully synthetic/fake work order data. It does not contain any private, confidential, employer-owned, resident, customer, vendor, or internal business data.

## Tech Stack

- Python
- SQLite
- SQL
- Streamlit
- Pandas
- Groq API
- Llama 3.3

## Database Tables

- Boroughs
- Developments
- Vendors
- Statuses
- WorkOrders
- Invoices

## Key Features

- Converts natural language questions into SQL
- Runs generated SQL against a SQLite database
- Displays query results in a table
- Shows basic charts for numeric results
- Includes SQL safety validation
- Uses synthetic work order and invoice data
- Provides sample business questions for testing

## Example Questions

- Show pending work orders by borough and development
- Show all completed work orders in Manhattan borough in 2026
- Which vendor has the highest total invoice amount?
- Show total invoice amount by funding source
- Count work orders by status
- Show average invoice amount by vendor

## How to Run the Project

1. Install Python.

2. Install the required packages:

```bash
pip install -r requirements.txt
