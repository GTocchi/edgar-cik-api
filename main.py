from fastapi import FastAPI, HTTPException
import requests
import gzip
import ijson
import json
from io import BytesIO
from functools import lru_cache
from threading import Lock

app = FastAPI(title="EDGAR CIK/Ticker API (Dual-source, Cached)")

# ------------------------------------------------
# Config
# ------------------------------------------------
CIK_JSON_URL = "https://github.com/GTocchi/edgar-cik-api/raw/main/result_cik_keyed.json.gz"
TICKER_JSON_URL = "https://github.com/GTocchi/edgar-cik-api/raw/main/result_ticker_keyed.json.gz"

# ------------------------------------------------
# In-memory caches
# ------------------------------------------------
_cache_lock = Lock()
_cached_files = {}
_ticker_map = None  # preloaded dictionary for ticker lookups


# ------------------------------------------------
# Helpers
# ------------------------------------------------
def get_gzipped_data(url: str) -> bytes:
    """Download and cache a gzipped JSON file from GitHub."""
    with _cache_lock:
        if url not in _cached_files:
            print(f"Downloading {url}")
            resp = requests.get(url)
            resp.raise_for_status()
            _cached_files[url] = resp.content
        return _cached_files[url]


def load_ticker_map():
    """Load the ticker-keyed map into memory once."""
    global _ticker_map
    if _ticker_map is None:
        print("Loading ticker map into memory...")
        data_bytes = get_gzipped_data(TICKER_JSON_URL)
        with gzip.GzipFile(fileobj=BytesIO(data_bytes)) as f:
            _ticker_map = json.load(f)
        # Convert all keys to uppercase for case-insensitive lookup
        _ticker_map = {k.upper(): v for k, v in _ticker_map.items()}
        print(f"Loaded {_ticker_map and len(_ticker_map):,} tickers into memory.")
    return _ticker_map


# ------------------------------------------------
# Lookup functions
# ------------------------------------------------
@lru_cache(maxsize=1024)
def find_by_cik(cik: str):
    """Stream-search the CIK-keyed JSON for a single CIK."""
    data_bytes = get_gzipped_data(CIK_JSON_URL)
    with gzip.GzipFile(fileobj=BytesIO(data_bytes)) as f:
        parser = ijson.kvitems(f, "")
        for key, value in parser:
            if key == cik:
                return value
    return None


def find_by_ticker(ticker: str):
    """Return company info dict directly for a ticker (case-insensitive)."""
    ticker_map = load_ticker_map()
    ticker = ticker.upper()
    entry = ticker_map.get(ticker)
    if not entry:
        return []
    return [entry]  # wrap in a list for consistent return type


# ------------------------------------------------
# API Endpoints
# ------------------------------------------------
@app.get("/cik/{cik}")
def get_by_cik(cik: str):
    try:
        data = find_by_cik(cik)
        if not data:
            raise HTTPException(status_code=404, detail="CIK not found")
        return data
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
# Preload both datasets at startup
# ------------------------------------------------
@app.on_event("startup")
def preload_data():
    try:
        get_gzipped_data(CIK_JSON_URL)
        load_ticker_map()
        print("Cached both CIK and Ticker data at startup.")
    except Exception as e:
        print(f"Failed to preload data: {e}")
