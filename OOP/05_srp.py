"""
Week 4 – Object-Oriented Design
Code Example 05: Single Responsibility Principle

BEFORE: One class with four different reasons to change.
AFTER:  Four classes, each with exactly one reason to change.
"""

# ─── BEFORE: SRP Violation ────────────────────────────────────────────────────

class StudentReport_BAD:
    """
    This class has at least four reasons to change:
    1. Academic office changes GPA calculation rules
    2. Web team changes HTML template or styling
    3. DBA changes database schema
    4. IT team changes email server / format

    Any of these changes forces you to open and edit this file —
    risking breaking the other three concerns in the process.
    """

    def __init__(self, student):
        self.student = student

    def calculate_gpa(self):
        grades = self.student.get("grades", [])
        return sum(grades) / len(grades) if grades else 0.0

    def format_as_html(self):
        return f"""
        <html>
          <body>
            <h1>{self.student['name']}</h1>
            <p>GPA: {self.calculate_gpa()}</p>
          </body>
        </html>
        """

    def save_to_database(self):
        # database-specific code here
        print(f"Saving {self.student['name']} to DB...")

    def send_email(self, address: str):
        # email-server-specific code here
        print(f"Sending report to {address}...")


# ─── AFTER: SRP Applied ───────────────────────────────────────────────────────

class GPACalculator:
    """
    Single responsibility: calculate a student's GPA.
    Only the academic office can demand a change here.
    """
    def calculate(self, student: dict) -> float:
        grades = student.get("grades", [])
        return sum(grades) / len(grades) if grades else 0.0


class ReportFormatter:
    """
    Single responsibility: produce a formatted representation of a student report.
    Only the web/UI team can demand a change here.
    """
    def to_html(self, student: dict, gpa: float) -> str:
        return f"""
        <html>
          <body>
            <h1>{student['name']}</h1>
            <p>Programme: {student.get('programme', 'N/A')}</p>
            <p>GPA: {gpa:.2f}</p>
          </body>
        </html>
        """


class StudentRepository:
    """
    Single responsibility: persist and retrieve student records.
    Only the database team can demand a change here.
    """
    def save(self, student: dict) -> None:
        print(f"Saving {student['name']} to database...")

    def find_by_email(self, email: str) -> dict | None:
        print(f"Fetching student {email} from database...")
        return None


class EmailService:
    """
    Single responsibility: send emails.
    Only the IT/comms team can demand a change here.
    """
    def send(self, address: str, subject: str, body: str) -> None:
        print(f"[EMAIL → {address}] Subject: {subject}")


# Each class is independently testable, deployable, and modifiable.
