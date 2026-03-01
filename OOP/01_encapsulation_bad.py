"""
Week 4 – Object-Oriented Design
Code Example 01: Encapsulation — The Wrong Way

When state is public, anyone can violate the rules.
"""


class CourseRegistration:
    """
    BAD: All fields are public.
    Nothing stops callers from corrupting the state.
    """

    def __init__(self, max_capacity: int):
        self.max_capacity = max_capacity           # public — anyone can change it
        self.enrolled_students = []               # public list — anyone can append directly


# ── Demo of the problem ────────────────────────────────────────────────────────

registration = CourseRegistration(max_capacity=30)

# These all work — Python won't stop them — but they ALL break invariants:

# 1. Bypass capacity check:
for i in range(50):
    registration.enrolled_students.append(f"Student {i}")   # now 50 students in a 30-seat course

# 2. Destroy the capacity invariant:
registration.max_capacity = 9999                             # rule is gone

# 3. Add duplicates:
registration.enrolled_students.append("Alice")
registration.enrolled_students.append("Alice")              # Alice enrolled twice

print(f"Enrolled: {len(registration.enrolled_students)}")   # prints 52 — disaster
