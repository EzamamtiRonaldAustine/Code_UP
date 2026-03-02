"""
Week 4 – Object-Oriented Design
Code Example 06: Open/Closed Principle

BEFORE: Adding a new discount type requires editing working core logic.
AFTER:  Adding a new discount type requires only writing one new class.
"""

from abc import ABC, abstractmethod


# ─── BEFORE: OCP Violation ────────────────────────────────────────────────────

class DiscountService_BAD:
    """
    Every new customer type adds an elif.
    The method grows indefinitely.
    Every addition risks breaking the existing cases.
    """

    def calculate_discount(self, customer_type: str, amount: float) -> float:
        if customer_type == "student":
            return amount * 0.10
        elif customer_type == "staff":
            return amount * 0.20
        elif customer_type == "alumni":
            return amount * 0.15
        elif customer_type == "corporate":          # new requirement → edit this file
            return amount * 0.05
        else:
            return 0.0


# ─── AFTER: OCP Applied ───────────────────────────────────────────────────────

class DiscountPolicy(ABC):
    """
    The abstraction. The service will depend on this — not on concrete policies.
    """
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass


class StudentDiscount(DiscountPolicy):
    def calculate(self, amount: float) -> float:
        return amount * 0.10


class StaffDiscount(DiscountPolicy):
    def calculate(self, amount: float) -> float:
        return amount * 0.20


class AlumniDiscount(DiscountPolicy):
    def calculate(self, amount: float) -> float:
        return amount * 0.15


class CorporateDiscount(DiscountPolicy):
    """
    Adding this new type did NOT require touching DiscountService.
    StudentDiscount was not touched. StaffDiscount was not touched.
    We extended the system without modifying anything that already worked.
    """
    def calculate(self, amount: float) -> float:
        return amount * 0.05


class DiscountService:
    """
    Closed for modification: this class never needs to change when a new
    discount type is introduced.
    Open for extension: new behaviour is added by creating new DiscountPolicy subclasses.
    """
    def __init__(self, policy: DiscountPolicy) -> None:
        self._policy = policy

    def calculate_discount(self, amount: float) -> float:
        return self._policy.calculate(amount)


# ── Usage ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    service = DiscountService(StudentDiscount())
    print(f"Student discount: {service.calculate_discount(100)}")   # 10.0

    service = DiscountService(CorporateDiscount())
    print(f"Corporate discount: {service.calculate_discount(100)}") # 5.0
