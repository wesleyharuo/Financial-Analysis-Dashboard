"""
demo_data.py
------------
Generates realistic synthetic financial data for local testing
when Yahoo Finance is unreachable (e.g. CI, offline environments).
Run: python src/demo_data.py
"""

import json, os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

rng = np.random.default_rng(42)

COMPANIES = {
    "AAPL":  {"name": "Apple Inc.",                  "sector": "Technology",       "country": "USA", "currency": "USD", "mc": 2800e9, "pe": 28.5, "pb": 42.1, "roe": 1.60, "margin": 0.253, "gross": 0.441, "op_margin": 0.298, "cr": 0.94,  "qr": 0.90,  "de": 1.99, "rev_g": 0.063, "dy": 0.005, "beta": 1.24},
    "MSFT":  {"name": "Microsoft Corporation",       "sector": "Technology",       "country": "USA", "currency": "USD", "mc": 3100e9, "pe": 34.2, "pb": 13.8, "roe": 0.40, "margin": 0.357, "gross": 0.691, "op_margin": 0.435, "cr": 1.77,  "qr": 1.75,  "de": 0.38, "rev_g": 0.158, "dy": 0.007, "beta": 0.90},
    "GOOGL": {"name": "Alphabet Inc.",               "sector": "Communication",    "country": "USA", "currency": "USD", "mc": 2100e9, "pe": 22.1, "pb":  6.2, "roe": 0.28, "margin": 0.241, "gross": 0.555, "op_margin": 0.274, "cr": 2.10,  "qr": 2.08,  "de": 0.10, "rev_g": 0.084, "dy": 0.000, "beta": 1.06},
    "JPM":   {"name": "JPMorgan Chase & Co.",        "sector": "Financial",        "country": "USA", "currency": "USD", "mc":  560e9, "pe": 11.2, "pb":  1.9, "roe": 0.17, "margin": 0.280, "gross": 0.600, "op_margin": 0.320, "cr": None,  "qr": None,  "de": 1.20, "rev_g": 0.212, "dy": 0.022, "beta": 1.10},
    "RY":    {"name": "Royal Bank of Canada",        "sector": "Financial",        "country": "CAN", "currency": "CAD", "mc":  210e9, "pe": 12.8, "pb":  1.8, "roe": 0.14, "margin": 0.264, "gross": 0.620, "op_margin": 0.310, "cr": None,  "qr": None,  "de": 1.40, "rev_g": 0.073, "dy": 0.038, "beta": 0.82},
    "TD":    {"name": "Toronto-Dominion Bank",       "sector": "Financial",        "country": "CAN", "currency": "CAD", "mc":  150e9, "pe": 11.1, "pb":  1.5, "roe": 0.13, "margin": 0.235, "gross": 0.590, "op_margin": 0.285, "cr": None,  "qr": None,  "de": 1.55, "rev_g": 0.048, "dy": 0.042, "beta": 0.85},
    "CNR":   {"name": "Canadian National Railway",   "sector": "Industrials",      "country": "CAN", "currency": "CAD", "mc":   96e9, "pe": 20.4, "pb":  5.1, "roe": 0.25, "margin": 0.322, "gross": 0.560, "op_margin": 0.398, "cr": 0.55,  "qr": 0.50,  "de": 0.88, "rev_g": 0.021, "dy": 0.019, "beta": 0.74},
    "SHOP":  {"name": "Shopify Inc.",                "sector": "Technology",       "country": "CAN", "currency": "USD", "mc":   88e9, "pe": 68.3, "pb":  8.9, "roe": 0.13, "margin": 0.143, "gross": 0.497, "op_margin": 0.104, "cr": 9.40,  "qr": 9.35,  "de": 0.04, "rev_g": 0.262, "dy": 0.000, "beta": 1.68},
}

def make_price_series(ticker, mc, years=5):
    n = int(252 * years)
    base = mc / 1e10
    drift = 0.0003 + rng.normal(0, 0.0001)
    vol   = 0.015 + rng.uniform(0, 0.01)
    log_r = rng.normal(drift, vol, n)
    price = base * np.exp(np.cumsum(log_r))
    dates = pd.bdate_range(end=datetime.today(), periods=n)
    vol_base = mc / 5e13
    volume   = (vol_base * (1 + rng.normal(0, 0.3, n))).clip(1e4)
    df = pd.DataFrame({
        "Open":   (price * (1 - rng.uniform(0, 0.005, n))).round(2),
        "High":   (price * (1 + rng.uniform(0, 0.01,  n))).round(2),
        "Low":    (price * (1 - rng.uniform(0, 0.01,  n))).round(2),
        "Close":  price.round(2),
        "Volume": volume.astype(int),
    }, index=dates)
    df.index.name = "Date"
    df.to_csv(os.path.join(RAW_DIR, f"{ticker}_price.csv"))
    return df


def make_income(rev_base, margin, gross, op_margin, years=4):
    data = {}
    for i in range(years):
        yr = str(2024 - i)
        rev  = rev_base * (0.92 ** i)
        gp   = rev * gross * (1 + rng.normal(0, 0.01))
        op   = rev * op_margin * (1 + rng.normal(0, 0.01))
        ni   = rev * margin * (1 + rng.normal(0, 0.01))
        ebit = op * 1.08
        data[yr] = {
            "Total Revenue":                     round(rev),
            "Gross Profit":                      round(gp),
            "Operating Income":                  round(op),
            "EBITDA":                            round(ebit),
            "Net Income":                        round(ni),
            "Basic EPS":                         round(ni / (rev / 500), 2),
            "Diluted EPS":                       round(ni / (rev / 490), 2),
            "Research And Development":          round(rev * 0.07),
            "Selling General And Administration":round(rev * 0.12),
        }
    return data


def make_cashflow(rev_base, years=4):
    data = {}
    for i in range(years):
        yr  = str(2024 - i)
        op  = rev_base * 0.22 * (0.93 ** i)
        inv = -rev_base * 0.07 * (0.93 ** i)
        fin = -rev_base * 0.10 * (0.93 ** i)
        fcf = op + inv * 0.6
        data[yr] = {
            "Operating Cash Flow":  round(op),
            "Investing Cash Flow":  round(inv),
            "Financing Cash Flow":  round(fin),
            "Free Cash Flow":       round(fcf),
            "Capital Expenditure":  round(inv * 0.6),
            "End Cash Position":    round(abs(op) * 0.8),
        }
    return data


def make_balance(rev_base, de, cr, years=4):
    data = {}
    for i in range(years):
        yr      = str(2024 - i)
        assets  = rev_base * 1.4 * (1.06 ** (3 - i))
        equity  = assets / (1 + de) if de else assets * 0.6
        liab    = assets - equity
        data[yr] = {
            "Total Assets":                          round(assets),
            "Total Liabilities Net Minority Interest":round(liab),
            "Stockholders Equity":                   round(equity),
            "Current Assets":                        round(assets * 0.35),
            "Current Liabilities":                   round(assets * 0.25 / max(cr or 1, 0.1)),
            "Long Term Debt":                        round(liab * 0.55),
        }
    return data


def generate_all():
    all_data = {}
    for ticker, c in COMPANIES.items():
        rev_base = c["mc"] * 0.15
        all_data[ticker] = {
            "ticker": ticker,
            "info": {
                "name":             c["name"],
                "sector":           c["sector"],
                "industry":         c["sector"],
                "country":          c["country"],
                "currency":         c["currency"],
                "market_cap":       c["mc"],
                "pe_ratio":         c["pe"],
                "forward_pe":       round(c["pe"] * 0.92, 1),
                "pb_ratio":         c["pb"],
                "ps_ratio":         round(c["mc"] / rev_base, 2),
                "ev_ebitda":        round(c["pe"] * c["margin"] * 0.7, 1),
                "roe":              c["roe"],
                "roa":              round(c["roe"] * 0.35, 3),
                "profit_margin":    c["margin"],
                "gross_margin":     c["gross"],
                "operating_margin": c["op_margin"],
                "current_ratio":    c["cr"],
                "quick_ratio":      c["qr"],
                "debt_to_equity":   round(c["de"] * 100, 1),
                "revenue_growth":   c["rev_g"],
                "earnings_growth":  round(c["rev_g"] * 1.2, 3),
                "dividend_yield":   c["dy"],
                "beta":             c["beta"],
                "fiftyTwoWeekHigh": None,
                "fiftyTwoWeekLow":  None,
                "targetMeanPrice":  None,
            },
            "income_statement": make_income(rev_base, c["margin"], c["gross"], c["op_margin"]),
            "cash_flow":        make_cashflow(rev_base),
            "balance_sheet":    make_balance(rev_base, c["de"] or 0.5, c["cr"] or 1.2),
        }
        make_price_series(ticker, c["mc"])
        print(f"  Generated {ticker}")

    out = os.path.join(RAW_DIR, "financials.json")
    with open(out, "w") as f:
        json.dump(all_data, f, indent=2, default=str)
    print(f"\nDemo data saved to {out}")


if __name__ == "__main__":
    print("Generating demo data...\n")
    generate_all()
    print("\nDone. Run: python src/app.py")
