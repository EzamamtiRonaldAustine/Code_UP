from tkinter import *
from tkinter.ttk import Combobox
from datetime import datetime, timedelta
from PIL import Image, ImageTk

# Global variables
books = []  # List to store all books in the library
students = {}  # Dictionary to store student objects
pending_requests = []  # Stores requests for librarian approval

# base class for Librarians and Students.
class User:
    """Base class for User, can be Librarian or Student."""
    def __init__(self, username, password): # Encapsulated username, password
        self._username = username  
        self._password = password  

    # Getter
    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    def login(self, password):
        """Abstract login method."""
        raise NotImplementedError("Subclasses should implement this!") # Polymorphism: subclass should implement this method


class Librarian(User): #Inheriting from User
    """Librarian class inheriting from User."""
    def __init__(self, username, password):
        super().__init__(username, password)

    def login(self):
        """Check librarian credentials."""
        return self.username == "admin" and self.password == "admin"


class Student(User): #Inheriting from User
    """Student class inheriting from User."""
    def __init__(self, student_id, name, year_of_study, password="student"):
        super().__init__(student_id, password)  # Using student_id as username
        self.name = name
        self.year_of_study = year_of_study
        self.borrowed_books = []
        self.fine = 0 # Stores the student's fine for overdue books.

    def request_borrow_book(self, book):
        """Request to borrow a book."""
        if book not in [req['book'] for req in pending_requests if req['student'] == self]:
            pending_requests.append({'student': self, 'book': book, 'requested_date': datetime.now()})

    def borrow_book(self, book):
        """Borrow a book."""
        self.borrowed_books.append({
            'book': book,
            'borrowed_date': datetime.now(),
            'due_date': datetime.now() + timedelta(weeks=2)
        })

    def return_book(self, book):
        """Return a borrowed book."""
        for borrowed in self.borrowed_books:
            if borrowed['book'] == book:
                days_late = (datetime.now() - borrowed['due_date']).days
                if days_late > 0:
                    self.fine += days_late * 5000  # 5000 UGX per day
                self.borrowed_books.remove(borrowed) # Remove the returned book.

    @property
    def student_id(self):
        return self.username  # Encapsulated student_id
    
    def login(self, password):
        """Check student credentials."""
        return self.password == password 
    
# Library class that manages the books, students, 
# and borrowing activities. Static methods used for managing resources.
class Library:
    """Library class to manage books and students."""
    @staticmethod
    def add_book(isbn, title, author, genre):
        """Add a book to the library."""
        book = {
            "ISBN": isbn,
            "Title": title,
            "Author": author,
            "Genre": genre
        }
        books.append(book)

    @staticmethod
    def view_books():
        """View all books in the library."""
        return books

    @staticmethod
    def add_student(student_id, name, year_of_study):
        """Add a student to the library."""
        if student_id not in students:
            students[student_id] = Student(student_id, name, year_of_study)
            return True
        return False
    
    @staticmethod
    def delete_student(student_id):
        """Delete a student from the library."""
        if student_id in students:
            del students[student_id]
            return True
        return False

    @staticmethod
    def view_students():
        """View all registered students."""
        return [(student.student_id, student.name, student.year_of_study) for student in students.values()]

    @staticmethod
    def search_books(query):
        """Search for books by ISBN, Title, or Author."""
        results = []
        for book in books:
            if (query.lower() in book['ISBN'].lower() or
                query.lower() in book['Title'].lower() or
                query.lower() in book['Author'].lower()):
                results.append(book)
        return results

    @staticmethod
    def view_borrowed_books():
        """View all borrowed books."""
        borrowed_books_info = []
        for student_id, student in students.items():
            if student.borrowed_books:
                for borrowed in student.borrowed_books:
                    borrowed_books_info.append((student_id, borrowed['book'], borrowed['due_date'].strftime('%Y-%m-%d')))
        return borrowed_books_info

# Manual entries for initial library setup
def setup_library():
    """Setup initial data for the library."""
    # Creating a default librarian
    librarian = Librarian("admin", "admin")

    # Adding some initial books
    Library.add_book("0", "The Great Gatsby", "F. Scott Fitzgerald", "Fiction")
    Library.add_book("1", "To Kill a Mockingbird", "Harper Lee", "Fiction")
    Library.add_book("2", "Life", "Austine Black", "Mystery")
    
    # Adding some initial students
    Library.add_student("B1", "John Rambo", "1")
    Library.add_student("B2", "Will Smith", "2")
    Library.add_student("B3", "Peter Simpson", "3")

# setup function to initialize the library data
setup_library()


