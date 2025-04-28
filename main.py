# main.py

from bond import Bond
from calculator import calculate_ytm, calculate_duration, calculate_convexity
from portfolio import BondPortfolio


def main():
    portfolio = BondPortfolio()

    num_bonds = int(input("How many bonds do you want to add to the portfolio? "))

    for i in range(num_bonds):
        print(f"\n--- Enter details for Bond {i+1} ---")

        face_value = float(input("Enter face value of the bond: "))
        coupon_rate = float(
            input("Enter annual coupon rate (as decimal, e.g., 0.05 for 5%): ")
        )
        total_maturity = float(
            input("Enter total original maturity of the bond (years): ")
        )
        remaining_years = float(input("Enter years remaining to maturity: "))
        clean_price = float(input("Enter current clean price of the bond: "))
        payment_frequency = int(
            input("Enter payment frequency (e.g., 2 for semi-annual): ")
        )
        days_since_last_coupon = float(input("Enter days since last coupon payment: "))

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
