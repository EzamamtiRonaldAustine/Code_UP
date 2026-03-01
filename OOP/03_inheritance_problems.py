"""
Week 4 – Object-Oriented Design
Code Example 03: Problems with Deep Inheritance

Demonstrates the Fragile Base Class Problem and the
combinatorial explosion problem.
"""

# ── Part 1: The Fragile Base Class Problem ─────────────────────────────────────

class Animal:
    """
    A base class that calls an internal hook method.
    If a subclass overrides that hook, changes to this class
    can silently break the subclass.
    """
    def move(self):
        self._prepare_movement()     # calls internal hook
        print(f"{self.__class__.__name__} is moving")

    def _prepare_movement(self):
        print("Preparing to move (default)")


class Dog(Animal):
    def _prepare_movement(self):
        print("Dog: wagging tail and getting excited")   # overrides internal hook


# This works fine... for now.
d = Dog()
d.move()

# BUT: Someone later changes Animal._prepare_movement to require a speed parameter.
# Dog's override no longer matches. Dog breaks — and Dog's author didn't change anything.


# ── Part 2: The Combinatorial Explosion Problem ────────────────────────────────
#
# University student types. Using inheritance naively:

class Student: pass
class LocalStudent(Student): pass
class InternationalStudent(Student): pass
class PartTimeStudent(Student): pass

# Now we need a part-time international student...
class PartTimeInternationalStudent(InternationalStudent, PartTimeStudent): pass

# ...and a local part-time student...
class LocalPartTimeStudent(LocalStudent, PartTimeStudent): pass

# ...and a full-time local student on scholarship...
# Each combination needs a new class. With 3 independent dimensions
# (residency × enrolment × scholarship), you'd need up to 8 classes.
# Add a 4th dimension and it's 16. This doesn't scale.

# The composition solution:
class ResidencyStatus:
    """One dimension of variation, isolated."""
    LOCAL = "local"
    INTERNATIONAL = "international"

class EnrolmentMode:
    """Another dimension, independent."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"

class Student:
    """
    GOOD: Student has a residency and an enrolment mode.
    Adding a new dimension (e.g. ScholarshipStatus) means adding
    one new class — not doubling the hierarchy.
    """
    def __init__(self, name: str, residency: str, enrolment: str):
        self.name      = name
        self.residency = residency
        self.enrolment = enrolment

# Any combination is now trivially representable:
s = Student("Alice", ResidencyStatus.INTERNATIONAL, EnrolmentMode.PART_TIME)
