"""
transform.py
------------
Loads raw financial data and computes all ratios, growth metrics,
and structured DataFrames ready for the dashboard.
"""

import json
import os
import pandas as pd
import numpy as np

RAW_DIR  = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(PROC_DIR, exist_ok=True)


def safe(val, default=None):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return default
    return val


def pct(val):
    if val is None:
        return None
    try:
        return round(float(val) * 100, 2)
    except Exception:
        return None


def fmt_billions(val):
    if val is None:
        return None
    try:
        return round(float(val) / 1e9, 2)
    except Exception:
        return None


def load_raw() -> dict:
    path = os.path.join(RAW_DIR, "financials.json")
    with open(path) as f:
        return json.load(f)


def build_kpi_table(raw: dict) -> pd.DataFrame:
    rows = []
    for ticker, data in raw.items():
        info = data.get("info", {})
        if "error" in info:
            continue
        rows.append({
            "Ticker":           ticker,
            "Company":          info.get("name", ticker),
            "Sector":           info.get("sector", "N/A"),
            "Country":          info.get("country", "N/A"),
            "Currency":         info.get("currency", "USD"),
            "Market Cap ($B)":  fmt_billions(info.get("market_cap")),
            "P/E Ratio":        round(float(info["pe_ratio"]), 2) if info.get("pe_ratio") else None,
            "Forward P/E":      round(float(info["forward_pe"]), 2) if info.get("forward_pe") else None,
            "P/B Ratio":        round(float(info["pb_ratio"]), 2) if info.get("pb_ratio") else None,
            "P/S Ratio":        round(float(info["ps_ratio"]), 2) if info.get("ps_ratio") else None,
            "EV/EBITDA":        round(float(info["ev_ebitda"]), 2) if info.get("ev_ebitda") else None,
            "ROE (%)":          pct(info.get("roe")),
            "ROA (%)":          pct(info.get("roa")),
            "Net Margin (%)":   pct(info.get("profit_margin")),
            "Gross Margin (%)": pct(info.get("gross_margin")),
            "Op. Margin (%)":   pct(info.get("operating_margin")),
            "Current Ratio":    round(float(info["current_ratio"]), 2) if info.get("current_ratio") else None,
            "Quick Ratio":      round(float(info["quick_ratio"]), 2) if info.get("quick_ratio") else None,
            "Debt/Equity":      round(float(info["debt_to_equity"]) / 100, 2) if info.get("debt_to_equity") else None,
            "Revenue Growth (%)": pct(info.get("revenue_growth")),
            "Earnings Growth (%)": pct(info.get("earnings_growth")),
            "Dividend Yield (%)":  pct(info.get("dividend_yield")),
            "Beta":             round(float(info["beta"]), 2) if info.get("beta") else None,
            "52W High":         info.get("52w_high"),
            "52W Low":          info.get("52w_low"),
            "Analyst Target":   info.get("analyst_target"),
        })
    df = pd.DataFrame(rows).set_index("Ticker")
    df.to_csv(os.path.join(PROC_DIR, "kpi_table.csv"))
    return df


def build_income_statement(raw: dict, ticker: str) -> pd.DataFrame:
    data = raw.get(ticker, {}).get("income_statement", {})
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data).T
    df.index.name = "Period"
    df = df.apply(pd.to_numeric, errors="coerce")
    key_rows = [
        "Total Revenue", "Gross Profit", "Operating Income",
        "EBITDA", "Net Income", "Basic EPS", "Diluted EPS",
        "Research And Development", "Selling General And Administration",
    ]
    available = [r for r in key_rows if r in df.columns]
    df = df[available] if available else df
    df = df / 1e9
    df = df.round(3)
    df.to_csv(os.path.join(PROC_DIR, f"{ticker}_income.csv"))
    return df


def build_cash_flow(raw: dict, ticker: str) -> pd.DataFrame:
    data = raw.get(ticker, {}).get("cash_flow", {})
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data).T
    df.index.name = "Period"
    df = df.apply(pd.to_numeric, errors="coerce")
    key_rows = [
        "Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow",
        "Free Cash Flow", "Capital Expenditure", "End Cash Position",
    ]
    available = [r for r in key_rows if r in df.columns]
    df = df[available] if available else df
    df = df / 1e9
    df = df.round(3)
    df.to_csv(os.path.join(PROC_DIR, f"{ticker}_cashflow.csv"))
    return df


def build_balance_sheet(raw: dict, ticker: str) -> pd.DataFrame:
    data = raw.get(ticker, {}).get("balance_sheet", {})
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data).T
    df.index.name = "Period"
    df = df.apply(pd.to_numeric, errors="coerce")
    df = df / 1e9
    df = df.round(3)
    df.to_csv(os.path.join(PROC_DIR, f"{ticker}_balance.csv"))
    return df


def load_price_history(ticker: str) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, f"{ticker}_price.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df["MA50"]  = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()
    df["Returns"] = df["Close"].pct_change()
    df["Cumulative Return"] = (1 + df["Returns"]).cumprod() - 1
    return df


def transform_all() -> dict:
    raw = load_raw()
    result = {
        "kpis":    build_kpi_table(raw),
        "raw":     raw,
        "tickers": list(raw.keys()),
    }
    print("Transformed data ready.")
    return result


if __name__ == "__main__":
    transform_all()
    print("Done.")
