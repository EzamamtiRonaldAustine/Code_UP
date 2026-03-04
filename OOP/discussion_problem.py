"""
Week 4 – Object-Oriented Design
DISCUSSION PROBLEM

Instructions (groups of 3–4, 8 minutes, then 12 minutes class discussion):

Look at this class carefully. Then answer the four questions on the slides.

1. How many reasons does this class have to change? Name each one.
   Which stakeholder would ask for that change?

2. Identify every invariant in this code.
   Which ones does the class protect? Which are fragile or missing?

3. If you had to write automated tests for add_student(), what problems would
   you run into? What does that tell you about the design?

4. The system now needs SMS notifications in addition to email.
   Walk through every line you'd have to touch. What principle does this speak to?
"""


class StudentManager:
    """
    This class exists in a real university system.
    Look carefully before you judge — see if you can identify
    everything that is wrong before checking the discussion slides.
    """

    def __init__(self):
        self.students      = []                  # note: public
        self.db_connection = DatabaseConnection()
        self.email_client  = EmailClient()

    def add_student(self, name: str, email: str, programme: str, year: int):
        # validate
        if not name or not email:
            raise ValueError("Name and email are required")
        if year < 1 or year > 5:
            raise ValueError("Year must be between 1 and 5")
        if "@" not in email:
            raise ValueError("Invalid email address")

        # check for duplicate
        for student in self.students:
            if student["email"] == email:
                raise ValueError("A student with this email already exists")

        # create and store
        student = {
            "name":      name,
            "email":     email,
            "programme": programme,
            "year":      year,
            "courses":   [],
            "gpa":       0.0,
        }
        self.students.append(student)

        # save to database
        self.db_connection.execute(
            "INSERT INTO students VALUES (?, ?, ?, ?)",
            [name, email, programme, year]
        )

        # send welcome email
        self.email_client.send(
            to=email,
            subject="Welcome to UCU",
            body=f"Dear {name}, welcome to the {programme} programme at UCU."
        )

        return student

    def enroll_in_course(self, student_email: str, course_code: str):
        student = None
        for s in self.students:
            if s["email"] == student_email:
                student = s
                break

        if not student:
            raise ValueError("Student not found")

        if len(student["courses"]) >= 8:
            raise ValueError("Maximum course load reached (8 courses)")

        if course_code in student["courses"]:
            raise ValueError("Student is already enrolled in this course")

        student["courses"].append(course_code)

        self.db_connection.execute(
            "INSERT INTO enrollments VALUES (?, ?)",
            [student_email, course_code]
        )

    def calculate_gpa(self, student_email: str, grades: dict) -> float:
        student = None
        for s in self.students:
            if s["email"] == student_email:
                student = s
                break

        if not student:
            raise ValueError("Student not found")

        if not grades:
            raise ValueError("No grades provided")

        total = sum(grades.values())
        student["gpa"] = total / len(grades)

        # send notification
        self.email_client.send(
            to=student_email,
            subject="Your GPA Update",
            body=f"Your current GPA is {student['gpa']:.2f}"
        )

        # update database
        self.db_connection.execute(
            "UPDATE students SET gpa = ? WHERE email = ?",
            [student["gpa"], student_email]
        )

        return student["gpa"]

    def get_student_report(self, student_email: str) -> str:
        student = None
        for s in self.students:
            if s["email"] == student_email:
                student = s
                break

        if not student:
            raise ValueError("Student not found")

        return f"""
        <html>
            <body>
                <h1>{student['name']}</h1>
                <p>Programme: {student['programme']}</p>
                <p>Year: {student['year']}</p>
                <p>GPA: {student['gpa']:.2f}</p>
                <p>Courses: {', '.join(student['courses'])}</p>
            </body>
        </html>
        """


# ── Stub classes so the file runs ─────────────────────────────────────────────

class DatabaseConnection:
    def execute(self, query: str, params: list = None): pass

class EmailClient:
    def send(self, to: str, subject: str, body: str): pass
