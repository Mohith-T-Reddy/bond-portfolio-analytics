# portfolio.py


class BondPortfolio:
    def __init__(self):
        self.bonds = []

    def add_bond(self, bond, ytm, duration, convexity, accrued_interest):
        """
        Add a bond and its analytics to the portfolio.
        """
        clean_price = bond.price
        self.bonds.append(
            {
                "bond": bond,
                "ytm": ytm,
                "duration": duration,
                "convexity": convexity,
                "accrued_interest": accrued_interest,
                "clean_price": clean_price,
                "dirty_price": clean_price + accrued_interest,
            }
        )

    def total_clean_value(self):
        """
        Total market value of the portfolio based on clean prices.
        """
        return sum(bond_info["clean_price"] for bond_info in self.bonds)

    def total_dirty_value(self):
        """
        Total market value including accrued interest.
        """
        return sum(bond_info["dirty_price"] for bond_info in self.bonds)

    def calculate_weighted_ytm(self):
        """
        Weighted average YTM based on clean prices.
        """
        total_clean = self.total_clean_value()
        if not total_clean:
            return 0.0
        return (
            sum(bond_info["ytm"] * bond_info["clean_price"] for bond_info in self.bonds)
            / total_clean
        )

    def calculate_weighted_duration(self):
        """
        Weighted average modified duration based on clean prices.
        """
        total_clean = self.total_clean_value()
        if not total_clean:
            return 0.0
        return (
            sum(
                bond_info["duration"] * bond_info["clean_price"]
                for bond_info in self.bonds
            )
            / total_clean
        )

    def calculate_weighted_convexity(self):
        """
        Weighted average convexity based on clean prices.
        """
        total_clean = self.total_clean_value()
        if not total_clean:
            return 0.0
        return (
            sum(
                bond_info["convexity"] * bond_info["clean_price"]
                for bond_info in self.bonds
            )
            / total_clean
        )

    def display_portfolio_summary(self):
        """
        Print a full summary of the bond portfolio.
        """
        total_clean = self.total_clean_value()
        print("\n---- Portfolio Summary ----")
        print(f"Number of Bonds: {len(self.bonds)}")
        print(f"Total Clean Value: ${total_clean:,.2f}")
        print(f"Total Dirty Value: ${self.total_dirty_value():,.2f}")
        print(f"Weighted Average YTM: {self.calculate_weighted_ytm() * 100:.2f}%")
        print(
            f"Weighted Average Modified Duration: {self.calculate_weighted_duration():.4f} years"
        )
        print(f"Weighted Average Convexity: {self.calculate_convexity():.4f}")
