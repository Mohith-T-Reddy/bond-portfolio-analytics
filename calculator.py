# calculator.py


def calculate_ytm(bond, tol=1e-6, max_iter=1000, high_ytm_threshold=0.5):
    """
    Calculate bond's Yield to Maturity using Newton-Raphson with Bisection fallback if needed.
    """

    price = bond.price
    face_value = bond.face_value
    coupon = bond.get_coupon_payment()
    periods = bond.get_number_of_payments()
    freq = bond.payment_frequency
    years_remaining = bond.remaining_years

    # Smart starting guess
    approx_ytm = (coupon * freq + (face_value - price) / years_remaining) / (
        (face_value + price) / 2
    )
    ytm = approx_ytm

    # Helper to calculate bond price for a given ytm
    def bond_price(ytm_guess):
        bond_pv = 0
        for t in range(1, int(periods) + 1):
            cash_flow = coupon
            if t == int(periods):
                cash_flow += face_value
            bond_pv += cash_flow / (1 + ytm_guess / freq) ** t
        return bond_pv

    # Try Newton-Raphson
    try:
        for _ in range(max_iter):
            calculated_price = bond_price(ytm)

            # Approximate derivative numerically
            delta = 1e-6
            price_up = bond_price(ytm + delta)
            derivative = (price_up - calculated_price) / delta

            diff = price - calculated_price

            if abs(diff) < tol:
                periodic_ytm = ytm
                annualized_ytm = (1 + periodic_ytm / freq) ** freq - 1
                if annualized_ytm > high_ytm_threshold:
                    print(
                        "High YTM detected from Newton-Raphson. Recalculating using Bisection method..."
                    )
                    break
                return annualized_ytm

            ytm = ytm + diff / derivative

    except Exception:
        print("Newton-Raphson failed. Falling back to Bisection method.")

    # Now fallback to Bisection method
    low = 0.0001
    high = 1.0

    for _ in range(200):
        mid = (low + high) / 2
        mid_price = bond_price(mid)

        if abs(mid_price - price) < tol:
            periodic_ytm = mid
            annualized_ytm = (1 + periodic_ytm / freq) ** freq - 1
            return annualized_ytm

        if mid_price > price:
            low = mid
        else:
            high = mid

    # After max bisection iterations
    periodic_ytm = mid
    annualized_ytm = (1 + periodic_ytm / freq) ** freq - 1
    return annualized_ytm


def calculate_duration(bond, ytm):
    """
    Calculate the modified duration of the bond.
    """

    price = bond.price
    face_value = bond.face_value
    coupon = bond.get_coupon_payment()
    periods = bond.get_number_of_payments()
    freq = bond.payment_frequency
    ytm_periodic = ytm / freq

    macaulay_duration = 0
    for t in range(1, int(periods) + 1):
        time = t / freq  # time in years
        cash_flow = coupon
        if t == int(periods):
            cash_flow += face_value
        present_value = cash_flow / (1 + ytm_periodic) ** t
        macaulay_duration += time * present_value

    macaulay_duration = macaulay_duration / price
    modified_duration = macaulay_duration / (1 + ytm_periodic)

    return modified_duration


def calculate_convexity(bond, ytm):
    """
    Calculate the modified convexity of the bond.
    """

    price = bond.price
    face_value = bond.face_value
    coupon = bond.get_coupon_payment()
    periods = bond.get_number_of_payments()
    freq = bond.payment_frequency
    ytm_periodic = ytm / freq

    convexity = 0
    for t in range(1, int(periods) + 1):
        time = t / freq  # time in years
        cash_flow = coupon
        if t == int(periods):
            cash_flow += face_value
        present_value = cash_flow / (1 + ytm_periodic) ** t
        convexity += time * (time + (1 / freq)) * present_value

    convexity = convexity / (price * (1 + ytm_periodic) ** 2)

    return convexity
