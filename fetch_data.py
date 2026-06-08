"""
fetch_data.py
-------------
Fetches financial data from Yahoo Finance for a list of tickers.
Covers: price history, income statement, balance sheet, cash flow, key ratios.
"""

import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime

TICKERS = {
    "AAPL":  "Apple Inc.",
    "MSFT":  "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "JPM":   "JPMorgan Chase & Co.",
    "RY":    "Royal Bank of Canada",
    "TD":    "Toronto-Dominion Bank",
    "CNR":   "Canadian National Railway",
    "SHOP":  "Shopify Inc.",
}

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)


def fetch_price_history(ticker: str, period: str = "5y") -> pd.DataFrame:
    t = yf.Ticker(ticker)
    hist = t.history(period=period)
    hist.index = hist.index.tz_localize(None)
    return hist[["Open", "High", "Low", "Close", "Volume"]]


def fetch_financials(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    data = {}

    try:
        info = t.info
        data["info"] = {
            "name":             info.get("longName", ticker),
            "sector":           info.get("sector", "N/A"),
            "industry":         info.get("industry", "N/A"),
            "country":          info.get("country", "N/A"),
            "currency":         info.get("currency", "USD"),
            "market_cap":       info.get("marketCap"),
            "pe_ratio":         info.get("trailingPE"),
            "forward_pe":       info.get("forwardPE"),
            "pb_ratio":         info.get("priceToBook"),
            "ps_ratio":         info.get("priceToSalesTrailing12Months"),
            "ev_ebitda":        info.get("enterpriseToEbitda"),
            "roe":              info.get("returnOnEquity"),
            "roa":              info.get("returnOnAssets"),
            "profit_margin":    info.get("profitMargins"),
            "gross_margin":     info.get("grossMargins"),
            "operating_margin": info.get("operatingMargins"),
            "current_ratio":    info.get("currentRatio"),
            "quick_ratio":      info.get("quickRatio"),
            "debt_to_equity":   info.get("debtToEquity"),
            "revenue_growth":   info.get("revenueGrowth"),
            "earnings_growth":  info.get("earningsGrowth"),
            "dividend_yield":   info.get("dividendYield"),
            "beta":             info.get("beta"),
            "52w_high":         info.get("fiftyTwoWeekHigh"),
            "52w_low":          info.get("fiftyTwoWeekLow"),
            "analyst_target":   info.get("targetMeanPrice"),
        }
    except Exception as e:
        data["info"] = {"name": ticker, "error": str(e)}

    for attr, key in [
        ("income_stmt",   "income_statement"),
        ("balance_sheet", "balance_sheet"),
        ("cashflow",      "cash_flow"),
    ]:
        try:
            df = getattr(t, attr)
            if df is not None and not df.empty:
                df.columns = [str(c.date()) if hasattr(c, "date") else str(c) for c in df.columns]
                data[key] = df.fillna(0).to_dict()
            else:
                data[key] = {}
        except Exception:
            data[key] = {}

    return data


def fetch_all(tickers: dict = TICKERS) -> dict:
    all_data = {}
    for ticker, name in tickers.items():
        print(f"  Fetching {ticker} ({name})...")
        try:
            financials = fetch_financials(ticker)
            price_hist = fetch_price_history(ticker)
            price_hist.to_csv(os.path.join(RAW_DIR, f"{ticker}_price.csv"))
            all_data[ticker] = financials
            all_data[ticker]["ticker"] = ticker
        except Exception as e:
            print(f"  ERROR {ticker}: {e}")
            all_data[ticker] = {"ticker": ticker, "error": str(e)}

    out_path = os.path.join(RAW_DIR, "financials.json")
    with open(out_path, "w") as f:
        json.dump(all_data, f, indent=2, default=str)

    print(f"\nSaved to {out_path}")
    return all_data


if __name__ == "__main__":
    print("Fetching financial data...\n")
    fetch_all()
    print("Done.")
