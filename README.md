## Mapping CIKs, Entity Names and Tickers (last update October 2025)

## Company Identifier Misalignment
The **goal of this project** is to provide a unified, programmatic mapping between CIKs, tickers and entity names, enabling fast and bulk reconciliation of EDGAR filings with market data, **covering every registered company, fund, subsidiaries, trusts, funds and other entity that ever filed with the SEC.**

Data providers like Bloomberg identify entities through **name, ticker, and ISIN**, whereas the SEC's EDGAR system relies primarily on **name** and its unique **10-digit CIK identifier** (with occasional tickers, but no ISIN, CUSIP, LEI, etc.).  
This misalignment complicates reconciliation between Bloomberg/other data sources and EDGAR.

---

## Data Sources: SEC Files
Several SEC sources provide entities mapping information, including bulk data files recompiled nightly and made available via the [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces):

1) **companyfacts.zip**: 18,826 entities. Each record is a JSON file keyed by CIK (e.g., `CIK0002053927.json`) and includes CIK and name.  
2) **submissions.zip**: 927,405 entities. Each JSON file includes CIK, name, and ticker. Tickers are populated for 6,813 companies. 

Moreover an additional file used is:
3) **[company_tickers_exchange.json](https://www.sec.gov/files/company_tickers_exchange.json)**: 7,847 entities, including CIK, name, and ticker.  

**Coverage and consistency:**
- All 18,826 entities in `companyfacts.zip` are present in `submissions.zip`, but only **41% of company names match exactly** due to naming variations.  
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
To reconcile inconsistencies, a unified JSON dictionary was created using **CIK as the key**:  [result_merged.json](https://gtocchi.github.io/edgar_merged_json/result_merged.json)  

- Each record integrates entities names and tickers from all three sources when available.
- Ensures the most complete representation of each entity and facilitates cross-referencing between Bloomberg/data providers and SEC/EDGAR.

**Example entry for CIK `0000794685`:**

```json
"0000794685": {
  "primary_ticker": "GAB",
  "secondary_securities": ["GAB-PG", "GAB-PH", "GAB-PK"],
  "denomination": ["GABELLI EQUITY TRUST INC"]
}
