# app.py

import streamlit as st
from bond import Bond
from calculator import calculate_ytm, calculate_duration, calculate_convexity
from portfolio import BondPortfolio
from live_data import fetch_bond_data


def main():
    st.set_page_config(page_title="Bond Portfolio Analytics", layout="wide")

    # ---- CUSTOM CSS for compact clean layout ----
    st.markdown(
        """
        <style>
        html, body, [class*="css"]  {
            font-size: 15px;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 1rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1600px;
        }
        header { 
            padding-top: 1.5rem; 
        }
        h1, h2, h3, h4 {
            font-size: 1.8rem !important;
            margin-bottom: 0.6rem;
            margin-top: 0.6rem;
        }
        .stMetric {
            padding: 0.3rem 0.5rem;
        }
        .stMetricValue {
            font-size: 1.3rem;
        }
        .stMetricLabel {
            font-size: 0.9rem;
        }
        .stExpanderHeader {
            font-size: 1.2rem !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # ---- Dashboard Title and Intro ----
    st.subheader("Bond Portfolio Analytics Dashboard")
    st.markdown(
        "Analyze individual bonds, compute YTM, Modified Duration, Convexity, and full portfolio metrics."
    )
    st.markdown("---")

    portfolio = BondPortfolio()

    num_bonds = st.number_input(
        "Number of Bonds to Add", min_value=1, max_value=50, step=1
    )

    for i in range(num_bonds):
        with st.expander(f"Bond {i+1} Input"):
            use_live_data = st.radio(
                f"Use Live Market Data for Bond {i+1}?",
                options=["No", "Yes"],
                index=0,
                horizontal=True,
            )

            face_value = 1000.0
            coupon_rate = 0.05
            bond_type = "fixed"
            market_reference_rate = 0.0
            quoted_spread = 0.0

            bond_ready = False

            if use_live_data == "Yes":
                symbol = st.text_input(
                    f"Enter Symbol for Bond {i+1} (e.g., SHY, TLT)"
                ).upper()

                if symbol:
                    live_data = fetch_bond_data(symbol)

                    if live_data["success"]:
                        st.success(f"Fetched Data for {symbol}")

                        col_fetch1, col_fetch2, col_fetch3 = st.columns(3)
                        with col_fetch1:
                            st.metric(
                                label="Fetched Price ($)",
                                value=(
                                    f"{live_data['price']:.2f}"
                                    if live_data["price"]
                                    else "N/A"
                                ),
                            )
                        with col_fetch2:
                            st.metric(
                                label="Fetched Yield (%)",
                                value=(
                                    f"{live_data['yield_estimate']*100:.2f}"
                                    if live_data["yield_estimate"]
                                    else "N/A"
                                ),
                            )
                        with col_fetch3:
                            st.metric(
                                label="Fetched Maturity",
                                value=(
                                    live_data["maturity_date"]
                                    if live_data["maturity_date"]
                                    else "Unknown"
                                ),
                            )

                        clean_price = (
                            live_data["price"]
                            if live_data["price"]
                            else st.number_input(
                                f"Clean Price (Manual Override) - Bond {i+1}",
                                value=100.0,
                            )
                        )
                        coupon_rate = (
                            live_data["yield_estimate"]
                            if live_data["yield_estimate"]
                            else st.number_input(
                                f"Coupon Rate (Decimal) (Manual Override) - Bond {i+1}",
                                value=0.05,
                            )
                        )
                        face_value = st.number_input(
                            f"Face Value - Bond {i+1}", value=1000.0
                        )

                        bond_ready = True
                    else:
                        st.error("Failed to fetch data. Please enter manually.")
                        use_live_data = "No"  # Switch back to manual

                else:
                    st.warning("Please enter a ticker symbol to fetch live data!")

            if use_live_data == "No":
                col_inputs = st.columns(3)
                with col_inputs[0]:
                    face_value = st.number_input(
                        f"Face Value - Bond {i+1}", value=1000.0
                    )
                with col_inputs[1]:
                    bond_type = st.selectbox(
                        f"Bond Type - Bond {i+1}", options=["fixed", "floating"]
                    )
                with col_inputs[2]:
                    clean_price = st.number_input(
                        f"Clean Price - Bond {i+1}", value=100.0
                    )

                if bond_type == "fixed":
                    coupon_rate = st.number_input(
                        f"Coupon Rate (Decimal) - Bond {i+1}", value=0.05
                    )
                    market_reference_rate = 0.0
                    quoted_spread = 0.0
                else:
                    market_reference_rate = st.number_input(
                        f"Market Reference Rate (Decimal) - Bond {i+1}", value=0.03
                    )
                    quoted_spread = st.number_input(
                        f"Quoted Spread (Decimal) - Bond {i+1}", value=0.01
                    )
                    coupon_rate = 0.0

                bond_ready = True

            if bond_ready:
                col_input1, col_input2, col_input3 = st.columns(3)

                with col_input1:
                    total_maturity = st.number_input(
                        f"Total Original Maturity (Years) - Bond {i+1}", value=10.0
                    )
                    payment_frequency = st.selectbox(
                        f"Payment Frequency - Bond {i+1}", options=[1, 2, 4], index=1
                    )  # Default to semi-annual (2)

                with col_input2:
                    remaining_years = st.number_input(
                        f"Years Remaining - Bond {i+1}", value=7.0
                    )
                    days_since_last_coupon = st.number_input(
                        f"Days Since Last Coupon - Bond {i+1}", value=30.0
                    )

                with col_input3:
                    buyer_seller = st.selectbox(
                        f"Buyer or Seller - Bond {i+1}", options=["buyer", "seller"]
                    )
                    day_count_convention = st.selectbox(
                        f"Day Count Convention - Bond {i+1}",
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
                    bond_type=bond_type,
                    market_reference_rate=market_reference_rate,
                    quoted_spread=quoted_spread,
                )

                # Calculate and Display Analytics
                ytm = calculate_ytm(bond)
                duration = calculate_duration(bond, ytm)
                convexity = calculate_convexity(bond, ytm)
                accrued_interest = bond.calculate_accrued_interest()

                st.info(f"Bond {i+1}: {bond_type.capitalize()} Rate")

                col_output1, col_output2, col_output3 = st.columns(3)
                with col_output1:
                    st.metric(label="YTM (%)", value=f"{ytm * 100:.2f}")
                    st.metric(label="Modified Duration (yrs)", value=f"{duration:.2f}")
                with col_output2:
                    st.metric(label="Convexity", value=f"{convexity:.2f}")
                    st.metric(
                        label="Accrued Interest ($)", value=f"{accrued_interest:.2f}"
                    )
                with col_output3:
                    st.metric(
                        label="Dirty Price ($)",
                        value=f"{clean_price + accrued_interest:.2f}",
                    )

                portfolio.add_bond(bond, ytm, duration, convexity, accrued_interest)

    st.markdown("---")

    # ---- Portfolio Summary ----
    if num_bonds > 0:
        st.subheader("Portfolio Summary")

        col7, col8, col9 = st.columns(3)
        with col7:
            st.metric(label="Number of Bonds", value=f"{len(portfolio.bonds)}")
            st.metric(
                label="Total Clean Value ($)",
                value=f"{portfolio.total_clean_value():,.2f}",
            )

        with col8:
            st.metric(
                label="Total Dirty Value ($)",
                value=f"{portfolio.total_dirty_value():,.2f}",
            )
            st.metric(
                label="Weighted Avg YTM (%)",
                value=f"{portfolio.calculate_weighted_ytm() * 100:.2f}",
            )

        with col9:
            st.metric(
                label="Weighted Duration (yrs)",
                value=f"{portfolio.calculate_weighted_duration():.2f}",
            )
            st.metric(
                label="Weighted Convexity",
                value=f"{portfolio.calculate_weighted_convexity():.2f}",
            )


if __name__ == "__main__":
    main()
