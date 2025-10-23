
from fastapi import FastAPI, HTTPException
import sqlite3
import json

app = FastAPI(title="EDGAR CIK Mapping API (SQLite)")
DB_PATH = "data.db"

# -----------------------
# Helper to get DB connection
# -----------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

# -----------------------
# CIK endpoint
# -----------------------
@app.get("/cik/{cik}")
def get_by_cik(cik: str):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM companies WHERE cik=?", (cik,)).fetchone()
    conn.close()

    if row:
        return {
            "cik": row["cik"],
            "primary_ticker": row["primary_ticker"],
            "secondary_securities": json.loads(row["secondary_securities"]),
            "denomination": json.loads(row["denomination"])
        }
    raise HTTPException(status_code=404, detail="CIK not found")

# -----------------------
# Ticker endpoint
# -----------------------
@app.get("/ticker/{ticker}")
def get_by_ticker(ticker: str):
    ticker = ticker.upper()
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM companies
        WHERE UPPER(primary_ticker)=?
           OR secondary_securities LIKE ?
    """, (ticker, f'%"{ticker}"%')).fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="Ticker not found")

    return [
        {
            "cik": r["cik"],
            "primary_ticker": r["primary_ticker"],
            "secondary_securities": json.loads(r["secondary_securities"]),
            "denomination": json.loads(r["denomination"])
        } for r in rows
    ]
