# calculator.py
from bond import Bond


def price_from_ytm(bond: Bond, ytm: float) -> float:
    """
    Compute the theoretical clean price of `bond` given an annualized yield-to-maturity.
    """
    freq = bond.payment_frequency
    coupon = bond.get_coupon_payment()
    periods = int(bond.get_number_of_payments())
    ytm_p = ytm / freq
    pv = 0.0
    discount = 1.0 / (1 + ytm_p)
    for t in range(periods):
        pv += coupon * (discount ** (t + 1))
    pv += bond.face_value * (discount**periods)
    return pv


def calculate_ytm(bond: Bond, tol=1e-6, max_iter=1000, high_ytm_threshold=0.5) -> float:
    """
    Calculate bond's Yield to Maturity using Newton-Raphson and Bisection fallback.
    Returns an annualized YTM.
    """
    price = bond.price
    face_value = bond.face_value
    coupon = bond.get_coupon_payment()
    periods = bond.get_number_of_payments()
    freq = bond.payment_frequency
    years_remaining = bond.remaining_years

    # Smart initial guess
    approx_ytm = (coupon * freq + (face_value - price) / years_remaining) / (
        (face_value + price) / 2
    )
    ytm = max(approx_ytm, 0.0001)  # Ensure positive initial guess

    # Newton-Raphson iteration
    for _ in range(max_iter):
        calc_price = price_from_ytm(bond, ytm)
        diff = price - calc_price
        if abs(diff) < tol:
            periodic = ytm
            return (1 + periodic / freq) ** freq - 1
        delta = 1e-6
        derivative = (price_from_ytm(bond, ytm + delta) - calc_price) / delta
        if derivative == 0:  # Avoid division by zero
            break
        ytm += diff / derivative
        if ytm <= 0 or ytm > high_ytm_threshold:  # Early exit for unreasonable values
            break

    # Bisection fallback
    low, high = 0.0001, min(high_ytm_threshold, 1.0)
    for _ in range(200):
        mid = (low + high) / 2
        mid_price = price_from_ytm(bond, mid)
        if abs(mid_price - price) < tol:
            periodic = mid
            return (1 + periodic / freq) ** freq - 1
        if mid_price > price:
            low = mid
        else:
            high = mid

    periodic = (low + high) / 2
    return (1 + periodic / freq) ** freq - 1


def calculate_duration(bond: Bond, ytm: float) -> float:
    """
    Modified duration = Macaulay duration / (1 + ytm_periodic).
    """
    price = bond.price
    coupon = bond.get_coupon_payment()
    periods = int(bond.get_number_of_payments())
    freq = bond.payment_frequency
    ytm_p = ytm / freq
    discount = 1.0 / (1 + ytm_p)

    macaulay = 0.0
    for t in range(periods):
        time = (t + 1) / freq
        pv = coupon * (discount ** (t + 1))
        macaulay += time * pv
    macaulay += (periods / freq) * bond.face_value * (discount**periods)
    macaulay /= price
    return macaulay / (1 + ytm_p)


def calculate_convexity(bond: Bond, ytm: float) -> float:
    """
    (Modified) convexity of the bond.
    """
    price = bond.price
    coupon = bond.get_coupon_payment()
    periods = int(bond.get_number_of_payments())
    freq = bond.payment_frequency
    ytm_p = ytm / freq
    discount = 1.0 / (1 + ytm_p)

    conv = 0.0
    for t in range(periods):
        time = (t + 1) / freq
        pv = coupon * (discount ** (t + 1))
        conv += time * (time + 1 / freq) * pv
    final_time = periods / freq
    conv += final_time * (final_time + 1 / freq) * bond.face_value * (discount**periods)
    return conv / (price * (1 + ytm_p) ** 2)


def calculate_dv01(bond: Bond, ytm: float) -> float:
    """
    Dollar value of a 1bp move: DV01 = Modified Duration * Price * 1bp
    """
    md = calculate_duration(bond, ytm)
    return md * bond.price * 0.0001


def calculate_effective_duration(bond: Bond, ytm: float, shift_bps: float) -> float:
    """
    Effective duration: (P(-Δy) - P(+Δy)) / (2 * P0 * Δy)
    shift_bps: in basis points; convert to decimal
    """
    shift = shift_bps / 10000
    P0 = bond.price
    P_plus = price_from_ytm(bond, ytm + shift)
    P_minus = price_from_ytm(bond, ytm - shift)
    return (P_minus - P_plus) / (2 * P0 * shift)


def calculate_effective_convexity(bond: Bond, ytm: float, shift_bps: float) -> float:
    """
    Effective convexity: (P(+Δy) + P(-Δy) - 2P0) / (P0 * (Δy)^2)
    shift_bps: in basis points; convert to decimal
    """
    shift = shift_bps / 10000
    P0 = bond.price
    P_plus = price_from_ytm(bond, ytm + shift)
    P_minus = price_from_ytm(bond, ytm - shift)
    return (P_plus + P_minus - 2 * P0) / (P0 * shift**2)
