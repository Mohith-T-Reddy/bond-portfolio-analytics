# live_data.py

import yfinance as yf


def fetch_bond_data(symbol):
    try:
        bond = yf.Ticker(symbol)

        info = bond.info

        price = info.get("regularMarketPrice")
        yield_estimate = info.get("yield")  # dividend yield estimate
        maturity_date = info.get(
            "bondMaturityDate", "Unknown"
        )  # rarely available for ETFs

        return {
            "price": price,
            "yield_estimate": yield_estimate,
            "maturity_date": maturity_date,
            "success": True,
        }
    except Exception as e:
        print(f"Error fetching bond data: {e}")
        return {"success": False}
