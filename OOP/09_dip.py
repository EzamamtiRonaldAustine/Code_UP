"""
Week 4 – Object-Oriented Design
Code Example 09: Dependency Inversion Principle

High-level modules (business logic) must not depend on low-level modules (infrastructure).
Both should depend on abstractions.

Key practical benefit: testability without infrastructure.
"""

from abc import ABC, abstractmethod


# ─── BEFORE: DIP Violation ────────────────────────────────────────────────────

class MySQLStudentRepository_Concrete:
    """A low-level, infrastructure module."""
    def save(self, student: dict) -> None:
        print(f"[MySQL] INSERT INTO students VALUES ({student})")

    def find_by_email(self, email: str) -> dict | None:
        print(f"[MySQL] SELECT * FROM students WHERE email='{email}'")
        return None


class StudentRegistrationService_BAD:
    """
    BAD: This high-level service directly depends on a concrete low-level class.
    To test this service: you need a live MySQL database.
    To switch databases: you must edit this class.
    """
    def __init__(self):
        self._repo = MySQLStudentRepository_Concrete()  # hardcoded dependency

    def register(self, student: dict) -> None:
        existing = self._repo.find_by_email(student["email"])
        if existing:
            raise ValueError("Student already registered")
        self._repo.save(student)
        print(f"Student {student['name']} registered successfully")


# ─── AFTER: DIP Applied ───────────────────────────────────────────────────────

class StudentRepository(ABC):
    """
    The abstraction that both the service and the implementations depend on.
    This is the 'inversion': instead of the service depending on MySQL,
    MySQL depends on this interface. The dependency points in the opposite direction.
    """
    @abstractmethod
    def save(self, student: dict) -> None: pass

    @abstractmethod
    def find_by_email(self, email: str) -> dict | None: pass


class MySQLStudentRepository(StudentRepository):
    """Production implementation."""
    def save(self, student: dict) -> None:
        print(f"[MySQL] Saving {student['name']}")

    def find_by_email(self, email: str) -> dict | None:
        print(f"[MySQL] Looking up {email}")
        return None


class InMemoryStudentRepository(StudentRepository):
    """
    Test implementation — no database required.
    Fast, isolated, controllable.
    """
    def __init__(self):
        self._store: dict = {}

    def save(self, student: dict) -> None:
        self._store[student["email"]] = student

    def find_by_email(self, email: str) -> dict | None:
        return self._store.get(email)


class StudentRegistrationService:
    """
    GOOD: Depends on the StudentRepository abstraction — not on MySQL.
    Can be tested with InMemoryStudentRepository.
    Can switch to PostgreSQL by writing PostgreSQLStudentRepository — service unchanged.
    """
    def __init__(self, repository: StudentRepository) -> None:
        self._repo = repository                    # injected dependency

    def register(self, student: dict) -> None:
        existing = self._repo.find_by_email(student["email"])
        if existing:
            raise ValueError(f"Student {student['email']} already registered")
        self._repo.save(student)
        print(f"Student {student['name']} registered successfully")


# ── Usage: production vs test ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Production ===")
    service = StudentRegistrationService(MySQLStudentRepository())
    service.register({"name": "Alice", "email": "alice@ucu.ac.ug"})

    print("\n=== Tests (no database) ===")
    repo    = InMemoryStudentRepository()
    service = StudentRegistrationService(repo)
    service.register({"name": "Bob", "email": "bob@ucu.ac.ug"})

    try:
        service.register({"name": "Bob", "email": "bob@ucu.ac.ug"})  # duplicate
    except ValueError as e:
        print(f"Caught: {e}")
