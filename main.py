from fastapi import FastAPI, HTTPException
import requests

app = FastAPI(title="EDGAR CIK Mapping API (Online JSON)")

# -----------------------
# Load JSON at startup
# -----------------------
JSON_URL = "https://raw.githubusercontent.com/GTocchi/edgar-cik-api/c0967407390470325225d8e99847115f0d99d622/result_merged.json.gz"
print("📥 Downloading JSON...")

try:
    resp = requests.get(JSON_URL)
    resp.raise_for_status()
    raw_data = resp.json()
except Exception as e:
    print("❌ Failed to download JSON:", e)
    raw_data = {}

print(f"✅ Loaded {len(raw_data)} entries")

# Build fast lookup dictionaries
cik_index = {}       # CIK -> info
ticker_index = {}    # ticker -> list of CIKs

for cik, info in raw_data.items():
    cik_index[cik] = info

    # Primary ticker
    pt = info.get("primary_ticker")
    if pt:
        ticker_index.setdefault(pt.upper(), []).append(cik)

    # Secondary tickers
    for sec in info.get("secondary_securities", []):
        ticker_index.setdefault(sec.upper(), []).append(cik)

print("✅ Indexes built")

# -----------------------
# CIK endpoint
# -----------------------
@app.get("/cik/{cik}")
def get_by_cik(cik: str):
    info = cik_index.get(cik)
    if info:
        return info
    raise HTTPException(status_code=404, detail="CIK not found")

# -----------------------
# Ticker endpoint
# -----------------------
@app.get("/ticker/{ticker}")
def get_by_ticker(ticker: str):
    ticker = ticker.upper()
    ciks = ticker_index.get(ticker, [])
    if not ciks:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return [cik_index[cik] for cik in ciks]
