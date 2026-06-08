#!/bin/bash
echo "Financial Analysis Dashboard"
echo "================================"

# Check if data exists
if [ ! -f "data/raw/financials.json" ]; then
    echo "No data found. Choose data source:"
    echo "  1) Fetch live data from Yahoo Finance"
    echo "  2) Use demo data (offline)"
    read -p "Enter choice [1/2]: " choice
    if [ "$choice" = "1" ]; then
        python src/fetch_data.py
    else
        python src/demo_data.py
    fi
fi

echo ""
echo "Starting dashboard at http://localhost:8050"
python src/app.py
