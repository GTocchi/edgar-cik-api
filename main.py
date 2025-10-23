from fastapi import FastAPI, HTTPException
import requests
import gzip
import ijson
from io import BytesIO
from functools import lru_cache
from threading import Lock

app = FastAPI(title="EDGAR CIK Streaming API (Render-safe)")

# ------------------------------------------------
# Config
# ------------------------------------------------
JSON_URL = "https://github.com/GTocchi/edgar-cik-api/raw/main/result_merged.json.gz"

# In-memory cache so we don’t re-download the file every request
_cached_bytes = None
_cache_lock = Lock()


# ------------------------------------------------
# Helper function: load gzipped JSON bytes once
# ------------------------------------------------
def get_gzipped_data() -> bytes:
    """Download and cache the gzipped JSON file from GitHub."""
    global _cached_bytes
    with _cache_lock:
        if _cached_bytes is None:
            resp = requests.get(JSON_URL)
            resp.raise_for_status()
            _cached_bytes = resp.content
        return _cached_bytes


# ------------------------------------------------
# Stream readers with caching
# ------------------------------------------------
@lru_cache(maxsize=1024)
def find_by_cik(cik: str):
    """Stream the JSON and return info for a single CIK."""
    data_bytes = get_gzipped_data()
    with gzip.GzipFile(fileobj=BytesIO(data_bytes)) as f:
        parser = ijson.kvitems(f, "")
        for key, value in parser:
            if key == cik:
                return value
    return None


@lru_cache(maxsize=512)
def find_by_ticker(ticker: str):
    """Stream the JSON and return all entries matching a ticker."""
    ticker = ticker.upper()
    matches = []

    data_bytes = get_gzipped_data()
    with gzip.GzipFile(fileobj=BytesIO(data_bytes)) as f:
        parser = ijson.kvitems(f, "")
        for key, value in parser:
            # Safely handle missing or None values
            primary = str(value.get("primary_ticker") or "").upper()
            if primary == ticker:
                matches.append(value)
                continue

            # Check secondary tickers safely
            for sec in value.get("secondary_securities", []) or []:
                if str(sec or "").upper() == ticker:
                    matches.append(value)
                    break
    return matches


# ------------------------------------------------
# API Endpoints
# ------------------------------------------------
@app.get("/cik/{cik}")
def get_by_cik(cik: str):
    try:
        data = find_by_cik(cik)
        if data:
            return data
        raise HTTPException(status_code=404, detail="CIK not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


@app.get("/ticker/{ticker}")
def get_by_ticker(ticker: str):
    try:
        data = find_by_ticker(ticker)
        if not data:
            raise HTTPException(status_code=404, detail="Ticker not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


# ------------------------------------------------
# Optional: Preload cache at startup (improves Render cold start)
# ------------------------------------------------
@app.on_event("startup")
def preload_data():
    try:
        get_gzipped_data()
        print("✅ Cached gzipped JSON data at startup.")
    except Exception as e:
        print(f"⚠️ Failed to preload data: {e}")
