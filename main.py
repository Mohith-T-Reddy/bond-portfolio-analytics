# main.py

from bond import Bond
from calculator import calculate_ytm, calculate_duration, calculate_convexity
from portfolio import BondPortfolio
from live_data import fetch_bond_data
from fred_fetch import fetch_yield_curve


def main():
    portfolio = BondPortfolio()

    # ---- Live Yield Curve Printout ----
    try:
        yield_curve = fetch_yield_curve()
        print("\nLive U.S. Treasury Yield Curve")
        print("---------------------------------------")
        for maturity, yield_value in yield_curve.items():
            if yield_value is not None:
                print(f"{maturity}: {yield_value:.2f}%")
            else:
                print(f"{maturity}: Data Unavailable")
        print("---------------------------------------\n")
    except Exception as e:
        print("Warning: Unable to fetch live U.S. Treasury Yield Curve.\n")

    num_bonds = int(input("How many bonds do you want to add to the portfolio? "))

    for i in range(num_bonds):
        print(f"\n--- Enter details for Bond {i+1} ---")

        # Live data or manual?
        print("\nDo you want to fetch bond details from live market data?")
        print("1 = Yes (fetch live)")
        print("2 = No (manual input)")
        live_choice = input("Enter choice (1 or 2, default 2): ") or "2"

        if live_choice == "1":
            symbol = input("Enter bond symbol (e.g., SHY, TLT): ").upper()
            live_data = fetch_bond_data(symbol)

            if live_data["success"]:
                print(f"\nFetched data for {symbol}:")
                print(f"Price: {live_data['price']}")
                print(f"Approx Yield: {live_data['yield_estimate']}")
                print(f"Maturity (if available): {live_data['maturity_date']}")

                face_value = float(input("Enter face value of the bond: "))
                clean_price = (
                    float(live_data["price"])
                    if live_data["price"]
                    else float(input("Enter clean price manually: "))
                )
                coupon_rate = (
                    float(live_data["yield_estimate"])
                    if live_data["yield_estimate"]
                    else float(input("Enter coupon rate manually (as decimal): "))
                )
                bond_type = "fixed"
                market_reference_rate = 0.0
                quoted_spread = 0.0

                total_maturity = float(
                    input("Enter total original maturity of the bond (years): ")
                )
                remaining_years = float(input("Enter years remaining to maturity: "))
                payment_frequency = int(
                    input("Enter payment frequency (e.g., 2 for semi-annual): ")
                )
                days_since_last_coupon = float(
                    input("Enter days since last coupon payment: ")
                )

            else:
                print("Failed to fetch live data. Proceeding manually.")
                live_choice = "2"  # fallback to manual

        if live_choice == "2":
            face_value = float(input("Enter face value of the bond: "))

            # Bond Type
            print("\nChoose Bond Type:")
            print("1 = Fixed Rate Bond")
            print("2 = Floating Rate Bond")
            bond_type_choice = input("Enter choice (1 or 2, default 1): ") or "1"

            if bond_type_choice == "2":
                bond_type = "floating"
                market_reference_rate = float(
                    input(
                        "Enter Market Reference Rate (as decimal, e.g., 0.03 for 3%): "
                    )
                )
                quoted_spread = float(
                    input("Enter Quoted Spread (as decimal, e.g., 0.01 for 100bps): ")
                )
                coupon_rate = 0.0
            else:
                bond_type = "fixed"
                coupon_rate = float(
                    input(
                        "Enter annual fixed coupon rate (as decimal, e.g., 0.05 for 5%): "
                    )
                )
                market_reference_rate = 0.0
                quoted_spread = 0.0

            total_maturity = float(
                input("Enter total original maturity of the bond (years): ")
            )
            remaining_years = float(input("Enter years remaining to maturity: "))
            clean_price = float(input("Enter current clean price of the bond: "))
            payment_frequency = int(
                input("Enter payment frequency (e.g., 2 for semi-annual): ")
            )
            days_since_last_coupon = float(
                input("Enter days since last coupon payment: ")
            )

        # Buyer or Seller
        print("\nAre you:")
        print("1 = Buyer")
        print("2 = Seller")
        buyer_seller_choice = input("Enter choice (1 or 2, default 1): ") or "1"

        if buyer_seller_choice == "2":
            buyer_or_seller = "seller"
        else:
            buyer_or_seller = "buyer"

        # Day Count Convention
        print("\nChoose Day Count Convention:")
        print("1 = 30/360")
        print("2 = Actual/360")
        print("3 = Actual/365")
        day_count_choice = input("Enter choice (1, 2, or 3, default 3): ") or "3"

        if day_count_choice == "1":
            day_count_convention = "30/360"
        elif day_count_choice == "2":
            day_count_convention = "actual/360"
        else:
            day_count_convention = "actual/365"

        # Create Bond object
        bond = Bond(
            face_value=face_value,
            coupon_rate=coupon_rate,
            total_maturity_years=total_maturity,
            remaining_years=remaining_years,
            clean_price=clean_price,
            payment_frequency=payment_frequency,
            days_since_last_coupon=days_since_last_coupon,
            buyer_or_seller=buyer_or_seller,
            day_count_convention=day_count_convention,
            bond_type=bond_type,
            market_reference_rate=market_reference_rate,
            quoted_spread=quoted_spread,
        )

        ytm = calculate_ytm(bond)
        duration = calculate_duration(bond, ytm)
        convexity = calculate_convexity(bond, ytm)
        accrued_interest = bond.calculate_accrued_interest()

        # Add to portfolio
        portfolio.add_bond(bond, ytm, duration, convexity, accrued_interest)

    # Display the portfolio summary
    portfolio.display_portfolio_summary()


if __name__ == "__main__":
    main()
