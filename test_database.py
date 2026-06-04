import sqlite3
import pandas as pd

DB_PATH = "Test1.db"

connection = sqlite3.connect(DB_PATH)

query = """
SELECT
    WorkOrders.WorkOrderID,
    Boroughs.BoroughName,
    Developments.DevelopmentName,
    Vendors.VendorName,
    Statuses.StatusName,
    WorkOrders.CreatedDate
FROM WorkOrders
JOIN Developments
    ON WorkOrders.DevelopmentID = Developments.DevelopmentID
JOIN Boroughs
    ON Developments.BoroughID = Boroughs.BoroughID
JOIN Vendors
    ON WorkOrders.VendorID = Vendors.VendorID
JOIN Statuses
    ON WorkOrders.StatusID = Statuses.StatusID
WHERE Statuses.StatusName = 'Pending'
LIMIT 10;
"""

df = pd.read_sql_query(query, connection)

print("Database connected successfully.")
print(df)

connection.close()