from fastapi import FastAPI, HTTPException
import requests
import gzip
from io import BytesIO
import ijson
from functools import lru_cache

app = FastAPI(title="EDGAR CIK Streaming API with Cache")

# GitHub raw URL to your compressed JSON
JSON_URL = "https://github.com/GTocchi/edgar-cik-api/raw/main/result_merged.json.gz"

# -----------------------
# Helper functions with caching
# -----------------------

@lru_cache(maxsize=1024)  # cache up to 1024 recently requested CIKs
def find_by_cik(cik: str):
    """Stream the JSON and return the info for a single CIK."""
    resp = requests.get(JSON_URL, stream=True)
    resp.raise_for_status()

    with gzip.GzipFile(fileobj=BytesIO(resp.content)) as f:
        parser = ijson.kvitems(f, "")
        for key, value in parser:
            if key == cik:
                return value
    return None

@lru_cache(maxsize=512)  # cache up to 512 recently requested tickers
def find_by_ticker(ticker: str):
    """Stream the JSON and return all entries matching a ticker."""
    ticker = ticker.upper()
    matches = []

    resp = requests.get(JSON_URL, stream=True)
    resp.raise_for_status()

    with gzip.GzipFile(fileobj=BytesIO(resp.content)) as f:
        parser = ijson.kvitems(f, "")
        for key, value in parser:
            # Check primary ticker
            if value.get("primary_ticker", "").upper() == ticker:
                matches.append(value)
                continue
            # Check secondary tickers
            for sec in value.get("secondary_securities", []):
                if sec.upper() == ticker:
                    matches.append(value)
                    break
    return matches

# -----------------------
# API Endpoints
# -----------------------

@app.get("/cik/{cik}")
def get_by_cik(cik: str):
    data = find_by_cik(cik)
    if data:
        return data
    raise HTTPException(status_code=404, detail="CIK not found")

@app.get("/ticker/{ticker}")
def get_by_ticker(ticker: str):
    data = find_by_ticker(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return data
