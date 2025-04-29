# app.py
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
from bond import Bond
from calculator import (
    calculate_dv01,
    calculate_effective_duration,
    calculate_ytm,
    calculate_duration,
    calculate_convexity,
)
from portfolio import BondPortfolio
from live_data import fetch_bond_data
from fred_fetch import fetch_rate, fetch_yield_curve


def main():
    st.set_page_config(page_title="Bond Portfolio Analytics", layout="wide")

    # ---- CUSTOM CSS for clean, compact layout ----
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-size: 15px;
        }
        .block-container {
            padding-top: 2.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1400px;
        }
        header {
            padding-top: 2.5rem;
        }
        h1, h2, h3, h4 {
            font-size: 1.7rem !important;
            margin-bottom: 0.5rem;
        }
        .stExpanderHeader {
            background-color: rgba(0, 100, 200, 0.2);
            border-radius: 0.5rem;
            padding: 0.25rem 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Live Market Data ----
    try:
        ten_series = fetch_rate("DGS10")
        two_series = fetch_rate("DGS2")
        latest_10y = ten_series.iloc[-1]
        prev_10y = ten_series.iloc[-2]
        prev_day = ten_series.index[-2].strftime("%a")
        latest_2y = two_series.iloc[-1]
        change = latest_10y - prev_10y
        spread = latest_10y - latest_2y
        yc = fetch_yield_curve()

        st.markdown("## Live Market Data")
        c1, c2, c3 = st.columns(3)
        c1.metric("10Y Treasury Yield", f"{latest_10y:.2f}%")
        c2.metric(f"Yield Change (vs {prev_day})", f"{change:+.2f} bps")
        c3.metric("2Y–10Y Spread", f"{spread:.2f} bps")

        fig, ax = plt.subplots(figsize=(9, 1.5))
        plt.style.use("dark_background")
        if yc:
            maturities = list(yc.keys())
            yields = list(yc.values())
            ax.grid(
                which="major", linestyle="--", linewidth=0.4, alpha=0.3, color="white"
            )
            ax.spines[["top", "right"]].set_visible(False)
            ax.spines[["bottom", "left"]].set_visible(True)
            ax.plot(maturities, yields, marker="o", color="#66ffff", linewidth=2)
            ax.fill_between(
                maturities, yields, min(yields) - 0.1, color="#66ffff", alpha=0.1
            )
            for m, y in zip(maturities, yields):
                ax.text(
                    m,
                    y + 0.03,
                    f"{y:.2f}%",
                    ha="center",
                    va="bottom",
                    color="white",
                    fontsize=8,
                )
            ax.set_xticks(maturities)
            ax.set_xticklabels(maturities, rotation=0, color="white", fontsize=9)
            ax.set_yticks([])
            ax.set_xlabel("Maturity", color="white", fontsize=10)
            ax.set_ylabel("Yield (%)", color="white", fontsize=10)
        st.pyplot(fig, clear_figure=True)
        st.caption(f"Last Updated: {datetime.now():%Y-%m-%d %H:%M:%S}")
        st.markdown("---")
    except Exception as e:
        st.warning(f"Unable to fetch live market data: {str(e)}")
        st.markdown("---")

    # ---- Bond Portfolio Inputs ----
    st.subheader("Bond Portfolio Analytics")
    portfolio = BondPortfolio()

    # Default templates with distinct values
    templates = [
        {
            "fv": 1000.0,
            "price": 980.0,
            "coupon": 0.045,
            "freq": 2,
            "total": 5,
            "remain": 5,
            "dslc": 15,
            "dcc": "actual/365",
            "type": "fixed",
            "mrr": 0.0,
            "spd": 0.0,
        },
        {
            "fv": 1000.0,
            "price": 1025.0,
            "coupon": 0.05,
            "freq": 2,
            "total": 7,
            "remain": 7,
            "dslc": 30,
            "dcc": "30/360",
            "type": "fixed",
            "mrr": 0.0,
            "spd": 0.0,
        },
        {
            "fv": 1000.0,
            "price": 995.0,
            "coupon": 0.0,
            "freq": 4,
            "total": 3,
            "remain": 3,
            "dslc": 10,
            "dcc": "actual/360",
            "type": "floating",
            "mrr": 0.025,
            "spd": 0.005,
        },
    ]

    count = st.number_input(
        "Number of Bonds to Add", min_value=1, max_value=20, value=3, step=1
    )
    for i in range(count):
        tpl = templates[min(i, len(templates) - 1)]
        with st.expander(f"Bond {i+1} Details", expanded=False):
            st.markdown(
                f"<div class='stExpanderHeader'>Bond {i+1} Details</div>",
                unsafe_allow_html=True,
            )
            # live = st.radio(
            #     "Fetch Live Data?",
            #     ["No", "Yes"],
            #     index=0,
            #     horizontal=True,
            #     key=f"live_{i}",
            # )

            # Initialize defaults
            fv = float(tpl["fv"])
            cp = float(tpl["price"])
            cr = float(tpl["coupon"])
            pf = int(tpl["freq"])
            tm = float(tpl["total"])
            ry = float(tpl["remain"])
            ds = int(tpl["dslc"])
            dcc = tpl["dcc"]
            btype = tpl["type"]
            mrr = float(tpl["mrr"])
            spd = float(tpl["spd"])

            # if live == "Yes":
            #     sym = st.text_input("Ticker", key=f"tic_{i}").upper()
            #     if sym:
            #         try:
            #             ld = fetch_bond_data(sym)
            #             if ld.get("success"):
            #                 cp = float(ld.get("price", cp))
            #                 if btype == "fixed":
            #                     cr = float(ld.get("yield_estimate", cr))
            #                 else:
            #                     spd = float(ld.get("yield_estimate", spd))
            #             else:
            #                 st.error("Live fetch failed; using default values.")
            #         except Exception as e:
            #             st.error(f"Error fetching live data: {str(e)}")
            #             live = "No"
            live = "No"  # Default to manual input mode

            if live == "No":
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    fv = st.number_input(
                        "Face Value",
                        value=fv,
                        step=0.1,
                        format="%.1f",
                        key=f"fv{i}",
                        min_value=0.0,
                    )
                    btype = st.selectbox(
                        "Bond Type",
                        ["fixed", "floating"],
                        index=["fixed", "floating"].index(btype),
                        key=f"bt{i}",
                    )
                with c2:
                    cp = st.number_input(
                        "Clean Price",
                        value=cp,
                        step=0.1,
                        format="%.1f",
                        key=f"cp{i}",
                        min_value=0.0,
                    )
                    pf = st.selectbox(
                        "Frequency (per year)",
                        [1, 2, 4],
                        index=[1, 2, 4].index(pf),
                        key=f"pf{i}",
                    )
                with c3:
                    tm = st.number_input(
                        "Total Maturity (yrs)",
                        value=tm,
                        step=0.1,
                        format="%.1f",
                        key=f"tm{i}",
                        min_value=0.1,
                    )
                    ry = st.number_input(
                        "Remaining Years",
                        value=ry,
                        step=0.1,
                        format="%.1f",
                        key=f"ry{i}",
                        min_value=0.0,
                    )
                with c4:
                    ds = st.number_input(
                        "Days Since Last Coupon",
                        value=ds,
                        step=1,
                        format="%d",
                        key=f"ds{i}",
                        min_value=0,
                    )
                    dcc = st.selectbox(
                        "Day Count",
                        ["30/360", "actual/360", "actual/365"],
                        index=["30/360", "actual/360", "actual/365"].index(dcc),
                        key=f"dc{i}",
                    )

                if btype == "fixed":
                    cr = st.number_input(
                        "Coupon Rate (decimal)",
                        value=cr,
                        step=0.001,
                        format="%.3f",
                        key=f"cr{i}",
                        min_value=0.0,
                    )
                    mrr = 0.0
                    spd = 0.0
                else:
                    mrr = st.number_input(
                        "Market Reference Rate (decimal)",
                        value=mrr,
                        step=0.001,
                        format="%.3f",
                        key=f"mr{i}",
                        min_value=0.0,
                    )
                    spd = st.number_input(
                        "Quoted Spread (decimal Oldsmobile",
                        value=spd,
                        step=0.001,
                        format="%.3f",
                        key=f"sp{i}",
                        min_value=0.0,
                    )
                    cr = 0.0

            shift_bps = st.number_input(
                "Shift for Eff Duration (bps)",
                min_value=1,
                max_value=1000,
                value=10,
                step=1,
                key=f"sh{i}",
            )

            try:
                bond = Bond(
                    face_value=fv,
                    coupon_rate=cr,
                    total_maturity_years=tm,
                    remaining_years=ry,
                    clean_price=cp,
                    payment_frequency=pf,
                    days_since_last_coupon=ds,
                    buyer_or_seller="buyer",
                    day_count_convention=dcc,
                    bond_type=btype,
                    market_reference_rate=mrr,
                    quoted_spread=spd,
                )

                ytm = calculate_ytm(bond)
                md = calculate_duration(bond, ytm)
                cv = calculate_convexity(bond, ytm)
                ai = bond.calculate_accrued_interest()
                dv = calculate_dv01(bond, ytm)
                ed = calculate_effective_duration(bond, ytm, shift_bps)

                st.markdown("**Bond Analytics**")
                o1, o2, o3 = st.columns(3)
                with o1:
                    st.metric("YTM (%)", f"{ytm*100:.2f}")
                    st.metric("Mod Duration (yrs)", f"{md:.2f}")
                    st.metric("DV01 ($)", f"{dv:.2f}")
                with o2:
                    st.metric("Convexity", f"{cv:.2f}")
                    st.metric("Eff Duration (yrs)", f"{ed:.2f}")
                with o3:
                    st.metric("Accrued Interest ($)", f"{ai:.2f}")
                    st.metric("Dirty Price ($)", f"{cp+ai:.2f}")

                portfolio.add_bond(bond, ytm, md, cv, ai)
            except Exception as e:
                st.error(f"Error calculating bond analytics: {str(e)}")

    st.markdown("---")
    if portfolio.bonds:
        st.subheader("Portfolio Summary")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric("# Bonds", len(portfolio.bonds))
            st.metric("Total Clean ($)", f"{portfolio.total_clean_value():,.2f}")
        with s2:
            st.metric("Total Dirty ($)", f"{portfolio.total_dirty_value():,.2f}")
            st.metric(
                "Wtd Avg YTM (%)", f"{portfolio.calculate_weighted_ytm()*100:.2f}"
            )
        with s3:
            st.metric(
                "Wtd Duration (yrs)", f"{portfolio.calculate_weighted_duration():.2f}"
            )
            st.metric(
                "Wtd Convexity", f"{portfolio.calculate_weighted_convexity():.2f}"
            )


if __name__ == "__main__":
    main()
