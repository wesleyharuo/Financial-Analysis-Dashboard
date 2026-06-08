"""
app.py
------
Financial Analysis Dashboard — Plotly Dash
Covers: Price History, Income Statement, Cash Flow, Balance Sheet,
        Ratio Analysis, Peer Comparison, and Screener.
"""

import os, sys, json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc

sys.path.insert(0, os.path.dirname(__file__))
from fetch_data import fetch_all, TICKERS
from transform import (
    load_raw, build_kpi_table, build_income_statement,
    build_cash_flow, build_balance_sheet, load_price_history,
)

# ── Theme ──────────────────────────────────────────────────────────────────
BG       = "#0f1117"
BG2      = "#161b27"
BORDER   = "#1e2130"
TEXT     = "#e2e8f0"
TEXT_MUT = "#64748b"
BLUE     = "#3b82f6"
GREEN    = "#22c55e"
RED      = "#ef4444"
AMBER    = "#f59e0b"
PURPLE   = "#a78bfa"
TEAL     = "#2dd4bf"

PLOT_LAYOUT = dict(
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT, size=12),
    xaxis=dict(gridcolor=BORDER, zeroline=False, showgrid=True),
    yaxis=dict(gridcolor=BORDER, zeroline=False, showgrid=True),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, font=dict(size=11)),
    margin=dict(l=12, r=12, t=36, b=12),
    hoverlabel=dict(bgcolor=BG2, bordercolor=BORDER, font=dict(color=TEXT, size=12)),
)

# ── Load data ──────────────────────────────────────────────────────────────
RAW_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "financials.json")

if not os.path.exists(RAW_PATH):
    print("Data not found. Fetching from Yahoo Finance...")
    fetch_all()

raw   = load_raw()
kpis  = build_kpi_table(raw)
tickers_available = [t for t in raw if "error" not in raw[t].get("info", {})]
TICKER_OPTIONS = [{"label": f"{t}  —  {raw[t]['info'].get('name', t)}", "value": t}
                  for t in tickers_available]

# ── Helpers ────────────────────────────────────────────────────────────────
def color_val(val, good_high=True):
    if val is None:
        return TEXT_MUT
    try:
        return GREEN if (float(val) >= 0) == good_high else RED
    except Exception:
        return TEXT_MUT

def kpi_card(label, value, sub="", good_high=True):
    if value is None:
        disp = "N/A"
        col  = TEXT_MUT
    else:
        try:
            disp = f"{float(value):,.2f}"
            col  = color_val(value, good_high)
        except Exception:
            disp = str(value)
            col  = TEXT
    return html.Div([
        html.Div(label, className="kpi-label"),
        html.Div(disp, className="kpi-value", style={"color": col}),
        html.Div(sub,  className="kpi-sub"),
    ], className="kpi-card")


def section(title):
    return html.Div(title, className="section-title")


# ── App init ───────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    title="Financial Analysis Dashboard",
    suppress_callback_exceptions=True,
)

# ── Layout ─────────────────────────────────────────────────────────────────
app.layout = html.Div(style={"backgroundColor": BG, "minHeight": "100vh", "color": TEXT}, children=[

    # Navbar
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("📊 Financial Analysis Dashboard", className="navbar-brand"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Overview",   href="#overview")),
                dbc.NavItem(dbc.NavLink("Financials", href="#financials")),
                dbc.NavItem(dbc.NavLink("Comparison", href="#comparison")),
            ], navbar=True),
            html.Span("Data: Yahoo Finance API", style={"color": TEXT_MUT, "fontSize": "11px"}),
        ], fluid=True),
        className="navbar", dark=True, sticky="top",
    ),

    dbc.Container(fluid=True, style={"padding": "24px 32px"}, children=[

        # ── Controls ──
        dbc.Row([
            dbc.Col([
                html.Label("Select Company", style={"fontSize": "12px", "color": TEXT_MUT, "marginBottom": "6px"}),
                dcc.Dropdown(
                    id="ticker-select",
                    options=TICKER_OPTIONS,
                    value=tickers_available[0] if tickers_available else None,
                    clearable=False,
                    style={"backgroundColor": BG2, "color": TEXT, "border": f"1px solid {BORDER}"},
                ),
            ], md=4),
            dbc.Col([
                html.Label("Price History Range", style={"fontSize": "12px", "color": TEXT_MUT, "marginBottom": "6px"}),
                dcc.RadioItems(
                    id="period-select",
                    options=[
                        {"label": "6M", "value": "6mo"},
                        {"label": "1Y", "value": "1y"},
                        {"label": "3Y", "value": "3y"},
                        {"label": "5Y", "value": "5y"},
                    ],
                    value="2y",
                    inline=True,
                    style={"color": TEXT, "fontSize": "13px", "paddingTop": "6px"},
                    inputStyle={"marginRight": "4px", "marginLeft": "12px"},
                ),
            ], md=4),
            dbc.Col([
                html.Label("Refresh Data", style={"fontSize": "12px", "color": TEXT_MUT, "marginBottom": "6px"}),
                html.Br(),
                dbc.Button("↻ Refresh", id="refresh-btn", color="primary", size="sm",
                           style={"backgroundColor": BLUE, "border": "none", "fontSize": "12px"}),
                html.Span(id="refresh-status", style={"color": TEXT_MUT, "fontSize": "11px", "marginLeft": "10px"}),
            ], md=4),
        ], className="mb-4"),

        # ── KPI cards ──
        html.Div(id="kpi-cards"),

        # ── Tabs ──
        dcc.Tabs(id="main-tabs", value="tab-price", className="custom-tabs", children=[
            dcc.Tab(label="Price & Returns",    value="tab-price",    className="tab", selected_className="tab--selected"),
            dcc.Tab(label="Income Statement",   value="tab-income",   className="tab", selected_className="tab--selected"),
            dcc.Tab(label="Cash Flow",          value="tab-cf",       className="tab", selected_className="tab--selected"),
            dcc.Tab(label="Balance Sheet",      value="tab-bs",       className="tab", selected_className="tab--selected"),
            dcc.Tab(label="Ratio Analysis",     value="tab-ratios",   className="tab", selected_className="tab--selected"),
            dcc.Tab(label="Peer Comparison",    value="tab-compare",  className="tab", selected_className="tab--selected"),
            dcc.Tab(label="Screener",           value="tab-screener", className="tab", selected_className="tab--selected"),
        ]),

        html.Div(id="tab-content", style={"marginTop": "20px"}),

    ]),

    # Footer
    html.Div([
        "Financial Analysis Dashboard  •  Data sourced from Yahoo Finance API  •  "
        "Built with Python, Plotly Dash, pandas  •  "
        "Wesley Haruo Kurosawa da Silva"
    ], className="footer"),
])


# ── Callbacks ──────────────────────────────────────────────────────────────

@app.callback(
    Output("refresh-status", "children"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_data(n):
    global raw, kpis, tickers_available
    try:
        fetch_all()
        raw  = load_raw()
        kpis = build_kpi_table(raw)
        tickers_available = [t for t in raw if "error" not in raw[t].get("info", {})]
        return "Updated successfully"
    except Exception as e:
        return f"Error: {str(e)[:40]}"


@app.callback(
    Output("kpi-cards", "children"),
    Input("ticker-select", "value"),
)
def update_kpi_cards(ticker):
    if not ticker or ticker not in raw:
        return []
    info = raw[ticker].get("info", {})
    mc   = info.get("market_cap")
    mc_s = f"${info.get('currency','USD')}"

    cards = [
        kpi_card("Market Cap",       f"{(mc/1e9):.1f}B" if mc else None,  info.get("currency","USD")),
        kpi_card("P/E Ratio",        info.get("pe_ratio"),     "Trailing 12M"),
        kpi_card("P/B Ratio",        info.get("pb_ratio"),     "Price / Book"),
        kpi_card("EV / EBITDA",      info.get("ev_ebitda"),    "Enterprise value"),
        kpi_card("ROE",              f"{(info['roe']*100):.1f}%" if info.get("roe") else None, "Return on equity"),
        kpi_card("Net Margin",       f"{(info['profit_margin']*100):.1f}%" if info.get("profit_margin") else None, "Net profit margin"),
        kpi_card("Current Ratio",    info.get("current_ratio"), "Liquidity"),
        kpi_card("Debt / Equity",    f"{(info['debt_to_equity']/100):.2f}" if info.get("debt_to_equity") else None, "Leverage", good_high=False),
        kpi_card("Revenue Growth",   f"{(info['revenue_growth']*100):.1f}%" if info.get("revenue_growth") else None, "YoY"),
        kpi_card("Dividend Yield",   f"{(info['dividend_yield']*100):.2f}%" if info.get("dividend_yield") else None, "Annual"),
        kpi_card("Beta",             info.get("beta"),          "Market sensitivity", good_high=False),
        kpi_card("Analyst Target",   info.get("analyst_target"), "Mean price target"),
    ]

    return [
        section("Key Performance Indicators"),
        dbc.Row([dbc.Col(c, md=2, sm=4, xs=6, className="mb-3") for c in cards]),
    ]


@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs",     "value"),
    Input("ticker-select", "value"),
    Input("period-select", "value"),
)
def render_tab(tab, ticker, period):
    if not ticker:
        return html.Div("Select a company to begin.", style={"color": TEXT_MUT})

    # ── Price & Returns ──────────────────────────────────────────────────
    if tab == "tab-price":
        hist = load_price_history(ticker)
        if hist.empty:
            return html.Div("Price data not available.", style={"color": TEXT_MUT})

        period_map = {"6mo": 126, "1y": 252, "2y": 504, "3y": 756, "5y": 1260}
        n = period_map.get(period, 504)
        hist = hist.iloc[-n:] if len(hist) > n else hist

        fig = make_subplots(
            rows=3, cols=1,
            row_heights=[0.55, 0.25, 0.20],
            shared_xaxes=True,
            vertical_spacing=0.04,
        )

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=hist.index, open=hist["Open"], high=hist["High"],
            low=hist["Low"], close=hist["Close"],
            name="Price",
            increasing_line_color=GREEN, decreasing_line_color=RED,
            increasing_fillcolor=GREEN, decreasing_fillcolor=RED,
        ), row=1, col=1)

        # Moving averages
        if "MA50" in hist.columns:
            fig.add_trace(go.Scatter(x=hist.index, y=hist["MA50"],  name="MA 50",
                                     line=dict(color=AMBER,  width=1.2)), row=1, col=1)
        if "MA200" in hist.columns:
            fig.add_trace(go.Scatter(x=hist.index, y=hist["MA200"], name="MA 200",
                                     line=dict(color=PURPLE, width=1.2)), row=1, col=1)

        # Volume
        colors = [GREEN if c >= o else RED
                  for c, o in zip(hist["Close"], hist["Open"])]
        fig.add_trace(go.Bar(
            x=hist.index, y=hist["Volume"], name="Volume",
            marker_color=colors, opacity=0.7,
        ), row=2, col=1)

        # Cumulative return
        if "Cumulative Return" in hist.columns:
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist["Cumulative Return"] * 100,
                name="Cumulative Return (%)",
                fill="tozeroy",
                line=dict(color=BLUE, width=1.5),
                fillcolor="rgba(59,130,246,0.12)",
            ), row=3, col=1)

        info = raw[ticker].get("info", {})
        name = info.get("name", ticker)
        fig.update_layout(
            **PLOT_LAYOUT,
            title=dict(text=f"{ticker}  —  {name}", font=dict(size=14, color=TEXT)),
            height=620,
            xaxis_rangeslider_visible=False,
            showlegend=True,
        )
        fig.update_yaxes(title_text="Price", row=1, col=1, tickfont=dict(size=10))
        fig.update_yaxes(title_text="Volume", row=2, col=1, tickfont=dict(size=10))
        fig.update_yaxes(title_text="Cum. Return %", row=3, col=1, tickfont=dict(size=10))

        return dcc.Graph(figure=fig, config={"displayModeBar": False})

    # ── Income Statement ─────────────────────────────────────────────────
    elif tab == "tab-income":
        df = build_income_statement(raw, ticker)
        if df.empty:
            return html.Div("Income statement data not available.", style={"color": TEXT_MUT})

        figs = []

        # Waterfall: latest period
        latest = df.iloc[0]
        wf_items = {
            "Total Revenue":     latest.get("Total Revenue", 0),
            "Gross Profit":      latest.get("Gross Profit", 0),
            "Operating Income":  latest.get("Operating Income", 0),
            "Net Income":        latest.get("Net Income", 0),
        }
        wf_items = {k: v for k, v in wf_items.items() if v != 0}

        if wf_items:
            labels = list(wf_items.keys())
            values = list(wf_items.values())
            prev   = values[0]
            measures = ["absolute"] + ["relative"] * (len(values) - 1)
            wf_vals  = [values[0]] + [values[i] - values[i-1] for i in range(1, len(values))]

            wf_fig = go.Figure(go.Waterfall(
                orientation="v",
                measure=measures,
                x=labels,
                y=wf_vals,
                connector=dict(line=dict(color=BORDER, width=1)),
                increasing=dict(marker_color=GREEN),
                decreasing=dict(marker_color=RED),
                totals=dict(marker_color=BLUE),
                texttemplate="%{y:.2f}B",
                textposition="outside",
                textfont=dict(color=TEXT, size=11),
            ))
            wf_fig.update_layout(
                **PLOT_LAYOUT,
                title=dict(text=f"Income Waterfall — {df.index[0]}  (USD billions)", font=dict(size=13)),
                height=340,
                showlegend=False,
            )
            figs.append(dcc.Graph(figure=wf_fig, config={"displayModeBar": False}))

        # Revenue & Net Income trend
        if "Total Revenue" in df.columns and "Net Income" in df.columns:
            trend_fig = go.Figure()
            trend_fig.add_trace(go.Bar(
                x=df.index, y=df["Total Revenue"],
                name="Total Revenue", marker_color=BLUE, opacity=0.85,
            ))
            trend_fig.add_trace(go.Bar(
                x=df.index, y=df["Net Income"],
                name="Net Income",
                marker_color=[GREEN if v >= 0 else RED for v in df["Net Income"]],
                opacity=0.85,
            ))
            if "Gross Profit" in df.columns:
                trend_fig.add_trace(go.Scatter(
                    x=df.index, y=df["Gross Profit"],
                    name="Gross Profit", mode="lines+markers",
                    line=dict(color=AMBER, width=2),
                ))
            trend_fig.update_layout(
                **PLOT_LAYOUT,
                barmode="group",
                title=dict(text="Revenue, Gross Profit & Net Income Trend  (USD billions)", font=dict(size=13)),
                height=360,
            )
            figs.append(dcc.Graph(figure=trend_fig, config={"displayModeBar": False}))

        # Margins trend
        margin_cols = [c for c in ["Gross Profit", "Operating Income", "Net Income"] if c in df.columns]
        rev_col = "Total Revenue"
        if margin_cols and rev_col in df.columns:
            mfig = go.Figure()
            colors_m = [GREEN, TEAL, BLUE]
            for col, col_color in zip(margin_cols, colors_m):
                margins = (df[col] / df[rev_col] * 100).round(1)
                mfig.add_trace(go.Scatter(
                    x=df.index, y=margins, name=f"{col} Margin %",
                    mode="lines+markers",
                    line=dict(color=col_color, width=2),
                    marker=dict(size=6),
                ))
            mfig.update_layout(
                **PLOT_LAYOUT,
                title=dict(text="Profit Margins Over Time  (%)", font=dict(size=13)),
                height=300,
                yaxis=dict(**PLOT_LAYOUT["yaxis"], ticksuffix="%"),
            )
            figs.append(dcc.Graph(figure=mfig, config={"displayModeBar": False}))

        # Raw table
        display_df = df.copy()
        display_df.index.name = "Period"
        display_df = display_df.reset_index()
        display_df = display_df.round(3)

        table = dash_table.DataTable(
            data=display_df.to_dict("records"),
            columns=[{"name": c, "id": c, "type": "numeric", "format": {"specifier": ".3f"}}
                     if c != "Period" else {"name": c, "id": c}
                     for c in display_df.columns],
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": BG, "color": TEXT, "fontSize": "12px",
                        "border": f"1px solid {BORDER}", "padding": "8px 12px"},
            style_header={"backgroundColor": BG2, "color": TEXT_MUT, "fontWeight": "600",
                          "fontSize": "11px", "textTransform": "uppercase"},
            page_size=8,
        )

        return html.Div([
            section("Income Statement  (USD billions)"),
            *figs,
            section("Raw Data"),
            table,
        ])

    # ── Cash Flow ────────────────────────────────────────────────────────
    elif tab == "tab-cf":
        df = build_cash_flow(raw, ticker)
        if df.empty:
            return html.Div("Cash flow data not available.", style={"color": TEXT_MUT})

        figs = []

        # Stacked bar: Operating / Investing / Financing
        cf_cols = [c for c in ["Operating Cash Flow", "Investing Cash Flow", "Financing Cash Flow"] if c in df.columns]
        if cf_cols:
            cf_colors = [GREEN, RED, AMBER]
            cf_fig = go.Figure()
            for col, col_color in zip(cf_cols, cf_colors):
                cf_fig.add_trace(go.Bar(
                    x=df.index, y=df[col], name=col,
                    marker_color=col_color, opacity=0.85,
                ))
            cf_fig.update_layout(
                **PLOT_LAYOUT,
                barmode="group",
                title=dict(text="Cash Flow by Activity  (USD billions)", font=dict(size=13)),
                height=360,
            )
            figs.append(dcc.Graph(figure=cf_fig, config={"displayModeBar": False}))

        # Free Cash Flow trend
        if "Free Cash Flow" in df.columns:
            fcf = df["Free Cash Flow"]
            fcf_fig = go.Figure(go.Bar(
                x=fcf.index, y=fcf,
                marker_color=[GREEN if v >= 0 else RED for v in fcf],
                name="Free Cash Flow",
                text=[f"{v:.2f}B" for v in fcf],
                textposition="outside",
                textfont=dict(color=TEXT, size=10),
            ))
            fcf_fig.update_layout(
                **PLOT_LAYOUT,
                title=dict(text="Free Cash Flow Trend  (USD billions)", font=dict(size=13)),
                height=300,
                showlegend=False,
            )
            figs.append(dcc.Graph(figure=fcf_fig, config={"displayModeBar": False}))

        return html.Div([section("Cash Flow Statement  (USD billions)"), *figs])

    # ── Balance Sheet ─────────────────────────────────────────────────────
    elif tab == "tab-bs":
        df = build_balance_sheet(raw, ticker)
        if df.empty:
            return html.Div("Balance sheet data not available.", style={"color": TEXT_MUT})

        figs = []

        # Assets / Liabilities / Equity
        bs_map = {
            "Total Assets":       ("Total Assets",       BLUE),
            "Total Liabilities":  ("Total Liabilities Net Minority Interest", RED),
            "Stockholders Equity":("Stockholders Equity", GREEN),
        }
        bs_cols = [(label, col, color) for label, (col, color) in bs_map.items() if col in df.columns]

        if bs_cols:
            bs_fig = go.Figure()
            for label, col, col_color in bs_cols:
                bs_fig.add_trace(go.Bar(
                    x=df.index, y=df[col], name=label,
                    marker_color=col_color, opacity=0.85,
                ))
            bs_fig.update_layout(
                **PLOT_LAYOUT,
                barmode="group",
                title=dict(text="Assets, Liabilities & Equity  (USD billions)", font=dict(size=13)),
                height=360,
            )
            figs.append(dcc.Graph(figure=bs_fig, config={"displayModeBar": False}))

        return html.Div([section("Balance Sheet  (USD billions)"), *figs])

    # ── Ratio Analysis ────────────────────────────────────────────────────
    elif tab == "tab-ratios":
        if ticker not in kpis.index:
            return html.Div("Ratio data not available.", style={"color": TEXT_MUT})

        row = kpis.loc[ticker]
        figs = []

        def gauge(title, value, lo, hi, suffix="", ref_lo=None, ref_hi=None):
            if value is None:
                return None
            try:
                val = float(value)
            except Exception:
                return None
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=val,
                title={"text": title, "font": {"size": 12, "color": TEXT_MUT}},
                number={"suffix": suffix, "font": {"size": 18, "color": TEXT}},
                gauge={
                    "axis": {"range": [lo, hi], "tickcolor": TEXT_MUT, "tickfont": {"size": 9}},
                    "bar": {"color": BLUE, "thickness": 0.25},
                    "bgcolor": BG2,
                    "bordercolor": BORDER,
                    "steps": [
                        {"range": [lo, hi * 0.33], "color": "rgba(34,197,94,0.12)"},
                        {"range": [hi * 0.33, hi * 0.66], "color": "rgba(245,158,11,0.10)"},
                        {"range": [hi * 0.66, hi], "color": "rgba(239,68,68,0.10)"},
                    ],
                },
            ))
            fig.update_layout(
                paper_bgcolor=BG, plot_bgcolor=BG,
                margin=dict(l=20, r=20, t=50, b=10),
                height=180, font=dict(color=TEXT),
            )
            return dcc.Graph(figure=fig, config={"displayModeBar": False})

        gauges_def = [
            ("P/E Ratio",     row.get("P/E Ratio"),       0, 60),
            ("P/B Ratio",     row.get("P/B Ratio"),       0, 20),
            ("EV/EBITDA",     row.get("EV/EBITDA"),       0, 40),
            ("Current Ratio", row.get("Current Ratio"),   0,  5),
            ("Quick Ratio",   row.get("Quick Ratio"),     0,  5),
            ("Debt/Equity",   row.get("Debt/Equity"),     0,  3),
        ]

        gauge_components = [g for _, val, lo, hi in gauges_def
                            if (g := gauge(_, val, lo, hi)) is not None]

        if gauge_components:
            figs.append(dbc.Row([
                dbc.Col(g, md=2, sm=4, xs=6) for g in gauge_components
            ]))

        # Spider / Radar chart comparing ratios across all tickers
        radar_metrics = ["ROE (%)", "Net Margin (%)", "Gross Margin (%)", "Op. Margin (%)"]
        radar_avail   = [m for m in radar_metrics if m in kpis.columns]
        if radar_avail and len(kpis) > 1:
            radar_fig = go.Figure()
            colors_r = [BLUE, GREEN, AMBER, PURPLE, TEAL, RED]
            for i, t in enumerate(kpis.index[:6]):
                vals = [kpis.loc[t, m] or 0 for m in radar_avail]
                radar_fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=radar_avail + [radar_avail[0]],
                    fill="toself",
                    name=t,
                    line=dict(color=colors_r[i % len(colors_r)], width=1.5),
                    fillcolor=colors_r[i % len(colors_r)].replace(")", ",0.08)").replace("rgb", "rgba")
                             if "rgb" in colors_r[i % len(colors_r)] else colors_r[i % len(colors_r)] + "14",
                ))
            radar_fig.update_layout(
                paper_bgcolor=BG, plot_bgcolor=BG,
                polar=dict(
                    bgcolor=BG2,
                    radialaxis=dict(visible=True, color=TEXT_MUT, gridcolor=BORDER),
                    angularaxis=dict(color=TEXT_MUT, gridcolor=BORDER),
                ),
                title=dict(text="Profitability Radar — All Companies", font=dict(size=13, color=TEXT)),
                font=dict(color=TEXT),
                margin=dict(l=40, r=40, t=50, b=40),
                height=420,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            )
            figs.append(dcc.Graph(figure=radar_fig, config={"displayModeBar": False}))

        return html.Div([section(f"Ratio Analysis — {ticker}"), *figs])

    # ── Peer Comparison ───────────────────────────────────────────────────
    elif tab == "tab-compare":
        if kpis.empty:
            return html.Div("No comparison data.", style={"color": TEXT_MUT})

        figs = []

        compare_metrics = [
            ("P/E Ratio",     "Valuation",     BLUE),
            ("ROE (%)",       "Profitability", GREEN),
            ("Net Margin (%)", "Margin",       TEAL),
            ("Debt/Equity",   "Leverage",      RED),
            ("Revenue Growth (%)", "Growth",   AMBER),
            ("Current Ratio", "Liquidity",     PURPLE),
        ]

        for metric, category, col_color in compare_metrics:
            if metric not in kpis.columns:
                continue
            data_m = kpis[metric].dropna().sort_values(ascending=False)
            if data_m.empty:
                continue
            bar_colors = [BLUE if t == ticker else col_color + "80" for t in data_m.index]
            fig_m = go.Figure(go.Bar(
                x=data_m.index,
                y=data_m.values,
                marker_color=bar_colors,
                text=[f"{v:.1f}" for v in data_m.values],
                textposition="outside",
                textfont=dict(color=TEXT, size=10),
                name=metric,
            ))
            fig_m.update_layout(
                **PLOT_LAYOUT,
                title=dict(text=f"{metric}  —  Peer Comparison", font=dict(size=12)),
                height=260,
                showlegend=False,
                margin=dict(l=12, r=12, t=36, b=12),
            )
            figs.append(dcc.Graph(figure=fig_m, config={"displayModeBar": False}))

        grid = [dbc.Col(f, md=6, className="mb-3") for f in figs]
        return html.Div([section("Peer Comparison"), dbc.Row(grid)])

    # ── Screener ──────────────────────────────────────────────────────────
    elif tab == "tab-screener":
        if kpis.empty:
            return html.Div("No screener data.", style={"color": TEXT_MUT})

        display = kpis.reset_index()
        cols_show = [c for c in [
            "Ticker", "Company", "Sector",
            "Market Cap ($B)", "P/E Ratio", "P/B Ratio", "EV/EBITDA",
            "ROE (%)", "Net Margin (%)", "Gross Margin (%)",
            "Current Ratio", "Debt/Equity",
            "Revenue Growth (%)", "Dividend Yield (%)", "Beta",
        ] if c in display.columns]

        table = dash_table.DataTable(
            data=display[cols_show].round(2).to_dict("records"),
            columns=[{"name": c, "id": c} for c in cols_show],
            sort_action="native",
            filter_action="native",
            style_table={"overflowX": "auto"},
            style_cell={"backgroundColor": BG, "color": TEXT, "fontSize": "12px",
                        "border": f"1px solid {BORDER}", "padding": "8px 12px",
                        "whiteSpace": "nowrap"},
            style_header={"backgroundColor": BG2, "color": TEXT_MUT, "fontWeight": "600",
                          "fontSize": "11px", "textTransform": "uppercase",
                          "border": f"1px solid {BORDER}"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgba(255,255,255,0.02)"},
            ],
            page_size=15,
        )

        return html.Div([
            section("Company Screener — All Tickers"),
            html.P("Click column headers to sort. Use filter rows to screen.",
                   style={"color": TEXT_MUT, "fontSize": "12px", "marginBottom": "12px"}),
            table,
        ])

    return html.Div("Select a tab.", style={"color": TEXT_MUT})


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
