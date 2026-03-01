"""
Week 4 – Object-Oriented Design
Code Example 02: Encapsulation — The Right Way

The object owns its state and enforces its own invariants.
"""

from __future__ import annotations


class CourseRegistration:
    """
    GOOD: The object owns its invariants.

    Invariants this class guarantees at all times:
    1. max_capacity is always > 0
    2. enrolled count never exceeds max_capacity
    3. no student is enrolled more than once
    4. the internal list is never directly accessible for modification
    """

    def __init__(self, max_capacity: int) -> None:
        if max_capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self._max_capacity = max_capacity   # private — underscore convention in Python
        self._enrolled: list = []

    # ── Public interface ───────────────────────────────────────────────────────

    def enroll(self, student: str) -> None:
        """Enroll a student, enforcing all invariants."""
        if len(self._enrolled) >= self._max_capacity:
            raise ValueError(f"Course is full. Maximum capacity is {self._max_capacity}.")
        if student in self._enrolled:
            raise ValueError(f"{student} is already enrolled in this course.")
        self._enrolled.append(student)

    def withdraw(self, student: str) -> None:
        """Remove a student from the course."""
        if student not in self._enrolled:
            raise ValueError(f"{student} is not enrolled in this course.")
        self._enrolled.remove(student)

    def get_enrolled(self) -> list:
        """
        Return a safe, read-only copy of the enrolled students.

        KEY POINT: We return list(self._enrolled), not self._enrolled.
        If we returned self._enrolled directly, a caller could do:
            reg.get_enrolled().append(student)
        ...and bypass all our validation. The defensive copy prevents this.
        """
        return list(self._enrolled)

    @property
    def enrolled_count(self) -> int:
        return len(self._enrolled)

    @property
    def available_seats(self) -> int:
        return self._max_capacity - len(self._enrolled)

    @property
    def is_full(self) -> bool:
        return len(self._enrolled) >= self._max_capacity


# ── Demo ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    reg = CourseRegistration(max_capacity=3)

    reg.enroll("Alice")
    reg.enroll("Bob")
    reg.enroll("Carol")

    try:
        reg.enroll("David")                      # raises: Course is full
    except ValueError as e:
        print(f"Caught: {e}")

    try:
        reg.enroll("Alice")                      # raises: Already enrolled
    except ValueError as e:
        print(f"Caught: {e}")

    # Attempting to modify via the getter — doesn't affect internal state
    snapshot = reg.get_enrolled()
    snapshot.append("Attacker")
    print(f"Internal count: {reg.enrolled_count}")   # still 3 — protected
