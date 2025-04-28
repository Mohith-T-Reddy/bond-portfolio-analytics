# bond.py


class Bond:
    def __init__(
        self,
        face_value,
        coupon_rate,
        total_maturity_years,
        remaining_years,
        clean_price,
        payment_frequency=2,
        days_since_last_coupon=0,
        buyer_or_seller="buyer",
        day_count_convention="actual/365",
        bond_type="fixed",  # NEW for FRN
        market_reference_rate=0.0,  # NEW for FRN
        quoted_spread=0.0,  # NEW for FRN
    ):
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.total_maturity_years = total_maturity_years
        self.remaining_years = remaining_years
        self.price = clean_price
        self.payment_frequency = payment_frequency
        self.days_since_last_coupon = days_since_last_coupon
        self.buyer_or_seller = buyer_or_seller.lower()
        self.day_count_convention = day_count_convention.lower()
        self.bond_type = bond_type.lower()
        self.market_reference_rate = market_reference_rate
        self.quoted_spread = quoted_spread

    def get_coupon_payment(self):
        if self.bond_type == "fixed":
            return self.face_value * self.coupon_rate / self.payment_frequency
        elif self.bond_type == "floating":
            effective_rate = self.market_reference_rate + self.quoted_spread
            return self.face_value * effective_rate / self.payment_frequency
        else:
            return 0

    def get_number_of_payments(self):
        return self.remaining_years * self.payment_frequency

    def calculate_days_in_period(self):
        if self.day_count_convention == "30/360":
            return 360 / self.payment_frequency
        elif self.day_count_convention == "actual/360":
            return 360 / self.payment_frequency
        else:  # default actual/365
            return 365 / self.payment_frequency

    def calculate_accrued_interest(self):
        coupon_payment = self.get_coupon_payment()
        days_in_period = self.calculate_days_in_period()

        accrued_interest = coupon_payment * (
            self.days_since_last_coupon / days_in_period
        )

        if self.buyer_or_seller == "seller":
            accrued_interest = -accrued_interest

        return accrued_interest
