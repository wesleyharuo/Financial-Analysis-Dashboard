
# Financial Analysis Dashboard

> Interactive financial analytics platform built with **Python · Plotly Dash · pandas · yfinance**  
> Covers S&P 500 and TSX-listed companies — real-time data, no paid API required.

<img width="2058" height="1265" alt="01_overview" src="https://github.com/user-attachments/assets/0308ac76-8861-4196-ad95-211fbb88646f" />
<img width="2046" height="1150" alt="04_peer_comparison" src="https://github.com/user-attachments/assets/8627d77a-f1d7-435d-ae46-966f9b1dbbce" />
<img width="2067" height="1106" alt="03_cash_flow" src="https://github.com/user-attachments/assets/3b6ab9a6-829f-4659-a42f-a788dda6fec1" />
<img width="2184" height="1134" alt="02_income_statement" src="https://github.com/user-attachments/assets/8ee4f2dc-cd33-43e5-aded-c402d520ebb4" />
---

## What This Project Does

This dashboard pulls live financial data from Yahoo Finance and delivers a full analysis across seven modules:

| Module | What It Shows |
|---|---|
| **Price & Returns** | Candlestick chart, MA50/MA200, volume, cumulative return |
| **Income Statement** | Revenue waterfall, margin trends, multi-year comparisons |
| **Cash Flow** | Operating / Investing / Financing CF, Free Cash Flow trend |
| **Balance Sheet** | Assets, liabilities, equity over time |
| **Ratio Analysis** | Gauge charts for 6 key ratios + profitability radar |
| **Peer Comparison** | Side-by-side bar charts across all tickers |
| **Screener** | Sortable, filterable table across all companies |

---

## Companies Covered

| Ticker | Company | Exchange |
|---|---|---|
| AAPL | Apple Inc. | NASDAQ (S&P 500) |
| MSFT | Microsoft Corporation | NASDAQ (S&P 500) |
| GOOGL | Alphabet Inc. | NASDAQ (S&P 500) |
| JPM | JPMorgan Chase & Co. | NYSE (S&P 500) |
| RY | Royal Bank of Canada | TSX / NYSE |
| TD | Toronto-Dominion Bank | TSX / NYSE |
| CNR | Canadian National Railway | TSX / NYSE |
| SHOP | Shopify Inc. | TSX / NYSE |

---

## Accounting Concepts Applied

This project applies the financial ratios and statements covered in the *** to real public company data.

### Valuation Ratios
| Ratio | Formula | What It Measures |
|---|---|---|
| **P/E Ratio** | Market Price / EPS | How much investors pay per dollar of earnings |
| **P/B Ratio** | Market Price / Book Value per Share | Premium over accounting value of assets |
| **EV/EBITDA** | Enterprise Value / EBITDA | Valuation independent of capital structure and taxes |

### Profitability Ratios
| Ratio | Formula | What It Measures |
|---|---|---|
| **ROE** | Net Income / Shareholders' Equity | Efficiency of equity in generating profit |
| **ROA** | Net Income / Total Assets | Efficiency of all assets in generating profit |
| **Net Margin** | Net Income / Revenue | Percentage of revenue retained as profit |
| **Gross Margin** | Gross Profit / Revenue | Revenue remaining after cost of goods sold |
| **Operating Margin** | Operating Income / Revenue | Efficiency of core business operations |

### Liquidity Ratios
| Ratio | Formula | What It Measures |
|---|---|---|
| **Current Ratio** | Current Assets / Current Liabilities | Ability to pay short-term obligations |
| **Quick Ratio** | (CA - Inventory) / CL | Liquidity without relying on inventory liquidation |

### Leverage Ratios
| Ratio | Formula | What It Measures |
|---|---|---|
| **Debt/Equity** | Total Debt / Shareholders' Equity | Financial leverage and capital structure risk |

### Growth Metrics
- **Revenue Growth (YoY)**: year-over-year change in total revenue
- **Earnings Growth (YoY)**: year-over-year change in EPS
- **Free Cash Flow**: Operating CF minus Capital Expenditure — cash available after maintaining assets

---

## Tech Stack

```
Python 3.12         — core language
yfinance            — Yahoo Finance API wrapper (no key required)
pandas              — data transformation and ratio calculations
NumPy               — numerical operations
Plotly              — interactive charts (candlestick, waterfall, radar, gauge)
Dash                — web application framework
dash-bootstrap-components — responsive layout
```

---

## Project Structure

```
finance-dashboard/
├── src/
│   ├── fetch_data.py     # Data ingestion from Yahoo Finance
│   ├── transform.py      # Ratio calculations and data modeling
│   └── app.py            # Dash application and chart callbacks
├── data/
│   ├── raw/              # Raw JSON and CSV from yfinance
│   └── processed/        # Cleaned DataFrames saved as CSV
├── assets/
│   └── style.css         # Dark theme styling
├── requirements.txt
└── README.md
```

---

## How to Run

```bash
# 1. Clone the repository
git clone https://github.com/wesleyharuofinance-dashboard.git
cd finance-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Fetch data (first run — takes ~60 seconds)
python src/fetch_data.py

# 4. Launch the dashboard
python src/app.py

# 5. Open in browser
# http://localhost:8050
```

Data refreshes automatically from Yahoo Finance each run. To add tickers, edit the `TICKERS` dict in `fetch_data.py`.

---

## Author

**Wesley Haruo Kurosawa da Silva**  
Analytics Engineer · Data Engineer  
Ontario, Canada

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Wesley_Haruo-0077B5?style=flat&logo=linkedin)](https://www.linkedin.com/in/wesleyharuo)
[![GitHub](https://img.shields.io/badge/GitHub-wesleyharuo-181717?style=flat&logo=github)](https://github.com/wesleyharuo)

---

*Data sourced from Yahoo Finance via the yfinance library. For educational and portfolio purposes only. Not financial advice.*
