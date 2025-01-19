from Library_system_Classes import *
# GUI pages for features
def open_add_book_page():
    """Open the page to add a book."""
    page = Toplevel()
    page.title("Add Book")
    set_background(page) # A helper function to set background for the page.

    Label(page, text="Enter ISBN:", font=("Arial", 12), bg="#F5F5DC").pack(pady=5)
    isbn_entry = Entry(page, width=30, font=("Arial", 12))
    isbn_entry.pack(pady=5)

    Label(page, text="Enter Book Title:", font=("Arial", 12), bg="#F5F5DC").pack(pady=5)
    title_entry = Entry(page, width=30, font=("Arial", 12))
    title_entry.pack(pady=5)

    Label(page, text="Enter Author Name:", font=("Arial", 12), bg="#F5F5DC").pack(pady=5)
    author_entry = Entry(page, width=30, font=("Arial", 12))
    author_entry.pack(pady=5)

    Label(page, text="Enter Genre:", font=("Arial", 12), bg="#F5F5DC").pack(pady=5)
    genre_entry = Entry(page, width=30, font=("Arial", 12))
    genre_entry.pack(pady=5)
    
    def add_book_action():
        """Action to add a book when the button is clicked."""
        isbn = isbn_entry.get()
        title = title_entry.get()
        author = author_entry.get()
        genre = genre_entry.get()
        Library.add_book(isbn, title, author, genre)
        Label(page, text=f"Book '{title}' added successfully!", fg="green", font=("Arial", 12)).pack(pady=10)

    Button(page, text="Add Book", command=add_book_action, bg="#5CB85C", fg="white", font=("Arial", 12), relief="flat", width=20).pack(pady=10)

def open_view_books_page():
    """Open the page to view all books."""
    page = Toplevel()
    page.title("View Books")
    set_background(page)

    Label(page, text="Books in Library:", font=("Arial", 12, "bold"), bg="#F5F5DC").pack(pady=10)

    for book in Library.view_books():
        book_info = f"ISBN: {book['ISBN']}, Title: {book['Title']}, Author: {book['Author']}, Genre: {book['Genre']}"
        Label(page, text=book_info, font=("Arial", 12), bg="#F5F5DC").pack(pady=5)

def open_add_student_page():
    """Open the page to add a student."""
    page = Toplevel()
    page.title("Add Student")
    set_background(page)

    Label(page, text="Enter Student ID:", font=("Arial", 12), bg="#F5F5DC").pack(pady=10)
    student_id_entry = Entry(page, width=30, font=("Arial", 12))
    student_id_entry.pack(pady=10)

    Label(page, text="Enter Student Name:", font=("Arial", 12), bg="#F5F5DC").pack(pady=10)
    student_name_entry = Entry(page, width=30, font=("Arial", 12))
    student_name_entry.pack(pady=10)

    Label(page, text="Enter Year of Study:", font=("Arial", 12), bg="#F5F5DC").pack(pady=10)
    year_of_study_entry = Entry(page, width=30, font=("Arial", 12))
    year_of_study_entry.pack(pady=10)

    def add_student_action():
        """Action to add a student when the button is clicked."""
        student_id = student_id_entry.get()
        student_name = student_name_entry.get()
        year_of_study = year_of_study_entry.get()
        if Library.add_student(student_id, student_name, year_of_study):
            Label(page, text=f"Student '{student_name}' added successfully!", fg="green", font=("Arial", 12)).pack(pady=10)
        else:
            Label(page, text=f"Student ID '{student_id}' already exists!", fg="red", font=("Arial", 12)).pack(pady=10)

    Button(page, text="Add Student", command=add_student_action, bg="#5CB85C", fg="white", font=("Arial", 12), relief="flat", width=20).pack(pady=10)

def open_delete_student_page():
    """Open the page to delete a student."""
    page = Toplevel()
    page.title("Delete Student")
    set_background(page)

    Label(page, text="Enter Student ID to Delete:", font=("Arial", 12), bg="#F5F5DC").pack(pady=10)
    student_id_entry = Entry(page, width=30, font=("Arial", 12))
    student_id_entry.pack(pady=10)

    def delete_student_action():
        """Action to delete a student when the button is clicked."""
        student_id = student_id_entry.get()
        if Library.delete_student(student_id):
            Label(page, text=f"Student ID '{student_id}' deleted successfully!", fg="green", font=("Arial", 12)).pack(pady=10)
        else:
            Label(page, text=f"Student ID '{student_id}' not found!", fg="red", font=("Arial", 12)).pack(pady=10)

    Button(page, text="Delete Student", command=delete_student_action, bg="#FF6347", fg="white", font=("Arial", 12), relief="flat", width=20).pack(pady=10) 
 
def open_search_books_page():
    """Open the page to search for books."""
    page = Toplevel()
    page.title("Search Books")
    set_background(page)

    Label(page, text="Enter Search Query (ISBN, Title, Author):", font=("Arial", 12), bg="#F5F5DC").pack(pady=10)
    search_entry = Entry(page, width=30, font=("Arial", 12))
    search_entry.pack(pady=10)

    def search_books_action():
        """Action to search for books when the button is clicked."""
        query = search_entry.get()
        results = Library.search_books(query)
        if results:
            for book in results:
                book_info = f"ISBN: {book['ISBN']}, Title: {book['Title']}, Author: {book['Author']}, Genre: {book['Genre']}"
                Label(page, text=book_info, font=("Arial", 12), bg="#F5F5DC").pack(pady=5)
        else:
            Label(page, text="No books found.", fg="red", font=("Arial", 12), bg="#F5F5DC").pack(pady=10)

    Button(page, text="Search Books", command=search_books_action, bg="#5CB85C", fg="white", font=("Arial", 12), relief="flat", width=20).pack(pady=10)
 
def open_view_students_page():
    """Open the page to view all students."""
    page = Toplevel()
    page.title("View Students")
    set_background(page)

    Label(page, text="Students:", font=("Arial", 12, "bold"), bg="#F5F5DC").pack(pady=10)
    for student_id, name, year_of_study in Library.view_students():
        Label(page, text=f"ID: {student_id} - Name: {name} - Year: {year_of_study}", font=("Arial", 12), bg="#F5F5DC").pack(pady=5)

def open_view_borrowed_books_page():
    """Open the page to view all borrowed books."""
    page = Toplevel()
    page.title("View Borrowed Books")
    set_background(page)

    Label(page, text="Borrowed Books:", font=("Arial",  12, "bold"), bg="#F5F5DC").pack(pady=10)
    borrowed_books = Library.view_borrowed_books()
    if borrowed_books:
        for student_id, book, due_date in borrowed_books:
            Label(page, text=f"Student ID: {student_id} - Book: {book} (Due: {due_date})", font=("Arial", 12), bg="#F5F5DC").pack(pady=5)
    else:
        Label(page, text="No books are currently borrowed.", font=("Arial", 12), fg="red", bg="#F5F5DC").pack(pady=10)

def open_return_book_page(student):
    """Open the page for a student to return a book."""
    page = Toplevel()
    page.title("Return Book")
    set_background(page)

    Label(page, text="Select a Book to Return:", font=("Arial", 12), bg="#F5F5DC").pack(pady=10)
    borrowed_books = [borrowed['book'] for borrowed in student.borrowed_books]
    book_combo = Combobox(page, values=borrowed_books, font=("Arial", 12), width=30)
    book_combo.pack(pady=10)

    def return_book_action():
        """Action to return a book when the button is clicked."""
        selected_book = book_combo.get()
        if selected_book:
            student.return_book(selected_book)
            Label(page, text=f"Book '{selected_book}' returned successfully!", fg="blue", font=("Arial", 12)).pack(pady=10)
            if student.fine > 0:
                Label(page, text=f"Fine due: {student.fine} UGX", fg="red", font=("Arial", 12)).pack(pady=5)
        else:
            Label(page, text="Please select a book.", fg="red", font=("Arial", 12)).pack(pady=10)

    Button(page, text="Return Book", command=return_book_action, bg="#5CB85C", fg="white", font=("Arial", 12), relief="flat", width=20).pack(pady=10)

def open_pending_requests_page():
    """Open the page to view pending book requests."""
    page = Toplevel()
    page.title("Pending Book Requests")
    set_background(page)

    Label(page, text="Pending Book Requests:", font=("Arial", 12, "bold"), bg="#F5F5DC").pack(pady=10)

    if not pending_requests:
        Label(page, text="No pending requests.", font=("Arial", 12), fg="red", bg="#F5F5DC").pack(pady=10)
        return

    for request in pending_requests:
        student_id = request['student'].student_id
        book = request['book']
        Label(page, text=f"Student ID: {student_id} - Book: {book}", font=("Arial", 12), bg="#F5F5DC").pack(pady=5)

        def authorize_request(req=request):
            """Authorize a book request."""
            req['student'].borrow_book(req['book'])
            pending_requests.remove(req)
            Label(page, text=f"Request for '{book}' by Student '{student_id}' approved!", fg="green", font=("Arial", 12)).pack(pady=5)

        def deny_request(req=request):
            """Deny a book request."""
            pending_requests.remove(req)
            Label(page, text=f"Request for '{book}' by Student '{student_id}' denied!", fg="red", font=("Arial", 12)).pack(pady=5)

        Button(page, text="Approve", command=authorize_request, bg="#5CB85C", fg="white", font=("Arial", 12), relief="flat", width=15).pack(side=LEFT, padx=10, pady=5)
        Button(page, text="Deny", command=deny_request, bg="#FF6347", fg="white", font=("Arial", 12), relief="flat", width=15).pack(side=LEFT, padx=10, pady=5)

def open_borrow_book_page(student):
    """Open the page for a student to request a book."""
    page = Toplevel()
    page.title("Borrow Book")
    set_background(page)

    Label(page, text="Select a Book to Request:", font=("Arial", 12), bg="#F5F5DC").pack(pady=10)
    book_combo = Combobox(page, values=[book['Title'] for book in Library.view_books()], font=("Arial", 12), width=30)
    book_combo.pack(pady=10)

    def borrow_book_request():
        """Action to request a book when the button is clicked."""
        selected_book = book_combo.get()
        if selected_book:
            student.request_borrow_book(selected_book)
            Label(page, text=f"Request to borrow '{selected_book}' sent for approval.", fg="blue", font=("Arial", 12)).pack(pady=10)
        else:
            Label(page, text="Please select a book.", fg="red", font=("Arial", 12)).pack(pady=10)

    Button(page, text="Request Borrow", command=borrow_book_request, bg="#5CB85C", fg="white", font=("Arial", 12), relief="flat", width=20).pack(pady=10)

def open_view_status_page(student):
    """Open the page to view borrowed books and fines."""
    page = Toplevel()
    page.title("View Status")
    set_background(page)

    Label(page, text="Borrowed Books and Fines:", font=("Arial", 12, "bold"), bg="#F5F5DC").pack(pady=10)
    if student.borrowed_books:
        for borrowed in student.borrowed_books:
            due_date = borrowed['due_date'].strftime('%Y-%m-%d')
            Label(page, text=f"Book: {borrowed['book']} (Due: {due_date})", font=("Arial", 12), bg="#F5F5DC").pack(pady=5)
    else:
        Label(page, text="No books borrowed.", font=("Arial", 12), fg="blue", bg="#F5F5DC").pack(pady=5)
    if student.fine > 0:
        Label(page, text=f"Outstanding fine: {student.fine} UGX", fg="red", font=("Arial", 12)).pack(pady=5)
    else:
        Label(page, text="No outstanding fines.", font=("Arial", 12), fg="green").pack(pady=5)

def set_background(window):
    """Set background color for the given window."""
    window.configure(bg="#F5F5DC")  # Beige color for all pages

