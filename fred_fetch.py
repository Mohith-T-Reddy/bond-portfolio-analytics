# fred_fetch.py

from fredapi import Fred
import os
import pandas as pd
import streamlit as st


def get_fred_connection():
    # Try environment variable first
    api_key = os.getenv("FRED_API_KEY")

    # If not found, fallback to hardcoded (for local testing)
    if not api_key:
        api_key = "30d8c514f7a153dff912ce2c41639b79"

    return Fred(api_key=api_key)


def fetch_rate(series_id):
    fred = get_fred_connection()
    data = fred.get_series_latest_release(series_id)
    return data


@st.cache_data(ttl=300)
def fetch_yield_curve():
    fred = get_fred_connection()
    maturities = {
        "1M": "DGS1MO",
        "3M": "DGS3MO",
        "6M": "DGS6MO",
        "1Y": "DGS1",
        "2Y": "DGS2",
        "3Y": "DGS3",
        "5Y": "DGS5",
        "7Y": "DGS7",
        "10Y": "DGS10",
        "20Y": "DGS20",
        "30Y": "DGS30",
    }
    rates = {}
    for label, series_id in maturities.items():
        try:
            ser = fred.get_series_latest_release(series_id)
            rates[label] = ser.iloc[-1]
        except Exception:
            rates[label] = None
    # Drop any None values so Streamlit chart doesn’t break
    return {k: v for k, v in rates.items() if v is not None}


if __name__ == "__main__":
    fred = get_fred_connection()

    # Fetch 10-Year US Treasury Yield
    ten_year_yield = fetch_rate("DGS10")

    latest_yield = ten_year_yield.iloc[-1]
    print(f"Live 10-Year Treasury Yield: {latest_yield:.2f}%")


# Common IDs:
# "DGS10" = 10-year US Treasury Yield
# "DGS2"  = 2-year US Treasury Yield
# "SOFR"  = Secured Overnight Financing Rate (new risk-free rate)
# "BAA10Y" = Baa Corporate Bond Spread 10Y
