## Mapping CIKs to Stock Names and Tickers for US Listed Stocks (last update August 2025)

## Company Identifier Misalignment
Data providers like Bloomberg identify companies through **name, ticker, and ISIN**, whereas the SEC's EDGAR system (that includes US-listed stocks) relies primarily on **company name** and its unique **10-digit CIK identifier** (with occasional tickers, but no ISIN, CUSIP, LEI, etc.).  
This misalignment complicates reconciliation between Bloomberg and EDGAR.

The **goal of this project** is to provide a unified, programmatic mapping between SEC CIKs and stock tickers/names, enabling fast and bulk reconciliation of EDGAR filings with market data.

---

## Data Sources: SEC Company Mapping Files
Several SEC sources provide company mapping information, including bulk data files recompiled nightly and made available via the [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces):

1) **companyfacts.zip**: 18,826 companies. Each record is a JSON file keyed by CIK (e.g., `CIK0002053927.json`) and includes CIK and company name.  
2) **submissions.zip**: 927,405 companies. Each JSON file includes CIK, company name, and ticker. Tickers are populated for 6,813 companies. 

Moreover an additional file used is:
3) **[company_tickers_exchange.json](https://www.sec.gov/files/company_tickers_exchange.json)**: 7,847 companies, including CIK, company name, and ticker.  

**Coverage and consistency:**
- All 18,826 companies in `companyfacts.zip` are present in `submissions.zip`, but only **41% of company names match exactly** due to naming variations.  
- All 7,847 companies in `company_tickers_exchange.json` are present in `submissions.zip`, with **87% exact name matches**.

---

## Additional Relevant Source: EDGAR Full-Index
The [EDGAR full-index](https://www.sec.gov/Archives/edgar/full-index/) archives SEC/EDGAR filings:  
- Provides comprehensive historical coverage dating back to 1993.  
- Each entry is identified by **company name** and **CIK**, allowing consistent linkage to other datasets.  

In the [cik-lookup-data.txt](https://www.sec.gov/Archives/edgar/cik-lookup-data.txt) file:
- Each line reports the **company name** and the **CIK**.  

---

## Integration Approach
To reconcile inconsistencies, a unified JSON dictionary was created using **CIK as the key**:  
- [result_merged.json](https://gtocchi.github.io/edgar_merged_json/result_merged.json)  

Each record integrates company names and tickers from all three sources when available, ensuring the most complete representation and easier cross-reference between Bloomberg and SEC/EDGAR.  

**Example entry for CIK `0000008177`:**

```json
"0000008177": {
  "name_submissions": "ATLANTIC AMERICAN CORP",
  "ticker": "AAME",
  "name_companyfacts": "ATLANTIC AMERICAN CORP",
  "name_json": "ATLANTIC AMERICAN CORP",
  "ticker_json": "AAME"
}
