from Library_system_Classes import *
from Library_system_methods import *
# Dashboard
def librarian_dashboard():
    """Display the librarian dashboard."""
    dash = Tk()
    dash.title("Librarian Dashboard")
    set_background(dash)

    Label(dash, text="Welcome to the Librarian Dashboard", font=("Arial", 16, "bold"), bg="#F5F5DC").pack(pady=20)
    Button(dash, text="Add Book", command=open_add_book_page, width=20).pack(pady=5)
    Button(dash, text="View Books", command=open_view_books_page, width=20).pack(pady=5)
    Button(dash, text="Search Books", command=open_search_books_page, width=20).pack(pady=5)
    Button(dash, text="Add Student", command=open_add_student_page, width=20).pack(pady=5)
    Button(dash, text="Delete Student", command=open_delete_student_page, width=20).pack(pady=5)
    Button(dash, text="View Students", command=open_view_students_page, width=20).pack(pady=5)
    Button(dash, text="View Borrowed Books", command=open_view_borrowed_books_page, width=20).pack(pady=5)
    Button(dash, text="View Pending Requests", command=open_pending_requests_page, width=20).pack(pady=5)
    Button(dash, text="Logout", command=lambda: [dash.destroy(), login_gui()], width=20, bg="red", fg="white").pack(pady=5)

    dash.mainloop()

def member_dashboard(student):
    """Display the student dashboard for a student."""
    dash = Tk()
    dash.title("Student Dashboard")
    set_background(dash)

    Label(dash, text=f"Welcome, {student.student_id}", font=("Arial", 16, "bold"), bg="#F5F5DC").pack(pady=20)
    Button(dash, text="Search Books", command=open_search_books_page, width=20).pack(pady=5)
    Button(dash, text="Borrow Book", command=lambda: open_borrow_book_page(student), width=20).pack(pady=5)
    Button(dash, text="Return Book", command=lambda: open_return_book_page(student), width=20).pack(pady=5)
    Button(dash, text="View Books", command=open_view_books_page, width=20).pack(pady=5)
    Button(dash, text="View Status", command=lambda: open_view_status_page(student), width=20).pack(pady=5)
    Button(dash, text="Logout", command=lambda: [dash.destroy(), login_gui()], width=20, bg="red", fg="white").pack(pady=5)

    dash.mainloop()

def login_gui():
    """Display the login GUI for the library system."""
    def attempt_login():
        """Attempt to log in based on user type."""
        user_type = user_type_combo.get().lower()  # Convert to lowercase for consistency
        user_id = user_id_entry.get()
        password = password_entry.get()

        if user_type == "librarian":
            librarian = Librarian(user_id, password)
            if librarian.login():
                window.destroy()
                librarian_dashboard()  # Open librarian dashboard
            else:
                Label(window, text="Invalid librarian credentials.", fg="red").grid(row=5, column=0, columnspan=2)

        elif user_type == "student":
            student = students.get(user_id)
            if student and student.login(password):
                window.destroy()
                member_dashboard(student)  # Open student/member dashboard
            else:
                Label(window, text="Invalid student ID or password.", fg="red").grid(row=5, column=0, columnspan=2)
        else:
            Label(window, text="Please select a valid user type.", fg="red").grid(row=5, column=0, columnspan=2)

    window = Tk()
    window.title("Library Login")
    window.configure(bg="#F5F5DC")

    Label(window, text="Library System Login", font=("Arial", 16, "bold"), bg="#F5F5DC").grid(row=0, column=0, columnspan=2, pady=10)
    Label(window, text="User  Type:", font=("Arial", 12), bg="#F5F5DC").grid(row=1, column=0, pady=5)

    user_type_combo = Combobox(window, values=["Librarian", "Student"], font=("Arial", 10))
    user_type_combo.grid(row=1, column=1, pady=5)
    user_type_combo.current(0)  # Set default value

    Label(window, text="User  ID:", font=("Arial", 12), bg="#F5F5DC").grid(row=2, column=0, pady=5)
    user_id_entry = Entry(window, width=25)
    user_id_entry.grid(row=2, column=1, pady=5)

    Label(window, text="Password:", font=("Arial", 12), bg="#F5F5DC").grid(row=3, column=0, pady=5)
    password_entry = Entry(window, show="*", width=25)
    password_entry.grid(row=3, column=1, pady=5)

    Button(window, text="Login", command=attempt_login, bg="#5CB85C", fg="white", font=("Arial", 12)).grid(row=4, column=1, pady=10)

    window.mainloop()

# Start the login GUI
login_gui()