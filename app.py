# app.py

import streamlit as st
from bond import Bond
from calculator import calculate_ytm, calculate_duration, calculate_convexity
from portfolio import BondPortfolio


def main():
    st.title("Bond Portfolio Analytics Tool")
    st.write("Enter bond details below and build your portfolio:")

    portfolio = BondPortfolio()

    num_bonds = st.number_input(
        "How many bonds do you want to add?", min_value=1, max_value=50, step=1
    )

    for i in range(num_bonds):
        st.header(f"Bond {i+1} Details")

        face_value = st.number_input(f"Face Value of Bond {i+1}", value=1000.0)
        coupon_rate = st.number_input(
            f"Annual Coupon Rate (as decimal, e.g., 0.05 for 5%) - Bond {i+1}",
            value=0.05,
        )
        total_maturity = st.number_input(
            f"Total Original Maturity (years) - Bond {i+1}", value=10.0
        )
        remaining_years = st.number_input(
            f"Years Remaining to Maturity - Bond {i+1}", value=7.0
        )
        clean_price = st.number_input(f"Current Clean Price - Bond {i+1}", value=1000.0)
        payment_frequency = st.selectbox(
            f"Payment Frequency - Bond {i+1}", options=[1, 2, 4]
        )
        days_since_last_coupon = st.number_input(
            f"Days Since Last Coupon Payment - Bond {i+1}", value=30.0
        )

        buyer_seller = st.selectbox(
            f"Are you the Buyer or Seller for Bond {i+1}?", options=["buyer", "seller"]
        )
        day_count_convention = st.selectbox(
            f"Day Count Convention for Bond {i+1}",
            options=["30/360", "actual/360", "actual/365"],
        )

        bond = Bond(
            face_value=face_value,
            coupon_rate=coupon_rate,
            total_maturity_years=total_maturity,
            remaining_years=remaining_years,
            clean_price=clean_price,
            payment_frequency=payment_frequency,
            days_since_last_coupon=days_since_last_coupon,
            buyer_or_seller=buyer_seller,
            day_count_convention=day_count_convention,
        )

        ytm = calculate_ytm(bond)
        duration = calculate_duration(bond, ytm)
        convexity = calculate_convexity(bond, ytm)
        accrued_interest = bond.calculate_accrued_interest()

        st.success(f"Bond {i+1} Analytics:")
        st.write(f"YTM: {ytm * 100:.2f}%")
        st.write(f"Modified Duration: {duration:.4f} years")
        st.write(f"Modified Convexity: {convexity:.4f}")
        st.write(f"Accrued Interest: ${accrued_interest:.2f}")
        st.write(f"Dirty Price: ${(clean_price + accrued_interest):.2f}")

        portfolio.add_bond(bond, ytm, duration, convexity, accrued_interest)

    if num_bonds > 0:
        st.header("Portfolio Summary")
        st.write(f"Number of Bonds: {len(portfolio.bonds)}")
        st.write(f"Total Clean Value: ${portfolio.total_clean_value():,.2f}")
        st.write(f"Total Dirty Value: ${portfolio.total_dirty_value():,.2f}")
        st.write(
            f"Weighted Average YTM: {portfolio.calculate_weighted_ytm() * 100:.2f}%"
        )
        st.write(
            f"Weighted Average Modified Duration: {portfolio.calculate_weighted_duration():.4f} years"
        )
        st.write(
            f"Weighted Average Convexity: {portfolio.calculate_weighted_convexity():.4f}"
        )


if __name__ == "__main__":
    main()
