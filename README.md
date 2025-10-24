# Mapping CIKs, Entity Names and Tickers (last update October 2025)

## Identification Misalignment
The **goal of this project** is to provide a unified, programmatic mapping between CIKs, tickers and entity names, enabling fast and bulk reconciliation of EDGAR filings with market data, **covering every registered company, fund, subsidiaries, trusts, funds and other entity that ever filed with the SEC.**

Data providers like Bloomberg identify entities through **name, ticker, and ISIN**, whereas the SEC's EDGAR system relies primarily on **name** and its unique **10-digit CIK identifier** (with occasional tickers, but no ISIN, CUSIP, LEI, etc.).  
This misalignment complicates reconciliation between Bloomberg/other data sources and EDGAR.

---

## Data Sources: SEC Files
Several SEC sources provide entities mapping information, including bulk data files recompiled nightly and made available via the [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) (kindly note that the following description is referred to the data as of August 2025, as an example):

1) **companyfacts.zip**: 18,826 entities. Each record is a JSON file keyed by CIK (e.g., `CIK0002053927.json`) and includes CIK and name.  
2) **submissions.zip**: 927,405 entities. Each JSON file includes CIK, name, and ticker. Tickers are populated for 6,813 entities. 

Moreover an additional file used is:
3) **[company_tickers_exchange.json](https://www.sec.gov/files/company_tickers_exchange.json)**: 7,847 entities, including CIK, name, and ticker.  

**Coverage and consistency:**
- All 18,826 entities in `companyfacts.zip` are present in `submissions.zip`, but only **41% of entities names match exactly** due to naming variations.  
- All 7,847 entities in `company_tickers_exchange.json` are present in `submissions.zip`, with **87% exact name matches**.

---

## Additional Relevant Source: EDGAR Full-Index
The [EDGAR full-index](https://www.sec.gov/Archives/edgar/full-index/) archives SEC/EDGAR filings:  
- Provides comprehensive historical coverage dating back to 1993.  
- Each entry is identified by **name** and **CIK**, allowing consistent linkage to other datasets.  

In the [cik-lookup-data.txt](https://www.sec.gov/Archives/edgar/cik-lookup-data.txt) file:
- Each line reports the **name** and the **CIK**.  

---

## Integration Approach
To reconcile inconsistencies, two JSON dictionary were created using **CIK as the key** and **ticker as the key**: 
- [result_cik_keyed.json.gz](https://github.com/GTocchi/edgar-cik-api/blob/main/result_cik_keyed.json.gz)
- [result_ticker_keyed.json.gz](https://github.com/GTocchi/edgar-cik-api/blob/main/result_ticker_keyed.json.gz)

In the JSON files:
- Each record integrates entities names, tickers and CIKs from all three sources when available.
- Ensures the most complete representation of each entity and facilitates cross-referencing between Bloomberg/data providers and SEC/EDGAR.

**Example entry for CIK `0000794685` in "result_cik_keyed":**

```json
"0000794685": {
  "primary_ticker": "GAB",
  "secondary_securities": ["GAB-PG", "GAB-PH", "GAB-PK"],
  "denomination": ["GABELLI EQUITY TRUST INC"]
}
```

**Example entry for ticker `GAB` in "result_ticker_keyed":**

```json
"GAB": {
  "secondary_securities": ["GAB-PG", "GAB-PH", "GAB-PK"],
  "denomination": ["GABELLI EQUITY TRUST INC"],
  "CIK": "0000794685",
}
```
## EDGAR CIK-Ticker API

I built an API allowing data retrieval and using an input either the **CIK** or the **ticker**.

**Base URL:** `https://edgar-cik-api.onrender.com`

**Endpoints:**

**1. Lookup by CIK**  
Retrieve entity information using the SEC CIK.  
`GET /cik/{cik}`

**Example in Python:**
```python
import requests

url = "https://edgar-cik-api.onrender.com/cik/0000320193"
response = requests.get(url)
data = response.json()
print(data)
```
```json
{
  "primary_ticker": "AAPL",
  "secondary_securities": ["AAPL-PG", "AAPL-PH"],
  "denomination": ["APPLE INC"]
}
```
**2. Lookup by ticker**  
Retrieve entity information using the ticker.  
`GET /ticker/{ticker}`

**Example in Python:**
```python
import requests

url = "https://edgar-cik-api.onrender.com/ticker/gab"
response = requests.get(url)
data = response.json()
print(data)
```

```json
{
  "secondary_securities": ["AAPL-PG", "AAPL-PH"],
  "denomination": ["GABELLI EQUITY TRUST INC"],
  "CIK": "0000320193",
}
```

**Note:** As the API is hosted on a free Render plan, cold starts may take a few seconds.
