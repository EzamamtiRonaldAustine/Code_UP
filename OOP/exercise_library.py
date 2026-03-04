"""
Week 4 – Object-Oriented Design
EXERCISE — Individual or Pairs (20 minutes)

The UCU Library System below has multiple design problems.
Redesign it using the principles covered today.

Your solution MUST include:
  1. At least 2 classes with clearly separated responsibilities
  2. At least 1 abstract base class that protects core logic from implementation details
  3. A Book class that owns its own availability invariant
  4. A brief comment on each class explaining its single responsibility

BONUS: Identify the invariant in return_book() that the current code ignores.
       What value could 'available' reach that should be impossible?

You do NOT need to provide fully working code.
Focus on structure, responsibilities, and invariants.
"""


# ─── CURRENT BROKEN IMPLEMENTATION ────────────────────────────────────────────

class Library:
    """
    A class that does everything. Find the violations.
    """

    def __init__(self):
        self.books   = []       # public — no protection
        self.members = []       # public
        self.db      = DatabaseConnection()

    def add_book(self, title: str, author: str, isbn: str, copies: int):
        book = {
            "title":     title,
            "author":    author,
            "isbn":      isbn,
            "copies":    copies,
            "available": copies,     # no class to own this invariant
        }
        self.books.append(book)
        self.db.execute(
            "INSERT INTO books VALUES (?, ?, ?, ?)",
            [title, author, isbn, copies]
        )

    def borrow_book(self, member_id: str, isbn: str):
        book = None
        for b in self.books:
            if b["isbn"] == isbn:
                book = b
                break

        if not book:
            raise ValueError("Book not found")

        if book["available"] == 0:
            raise ValueError("No copies available")

        book["available"] -= 1                   # no owner — just a dict update

        self.db.execute(
            "INSERT INTO loans VALUES (?, ?, ?)",
            [member_id, isbn, "today"]
        )

        # HTML generation mixed with borrowing logic:
        print(f"<html><p>You borrowed '{book['title']}'</p></html>")

    def return_book(self, member_id: str, isbn: str):
        book = None
        for b in self.books:
            if b["isbn"] == isbn:
                book = b
                break

        book["available"] += 1                   # ← BONUS: what invariant is missing here?
        #                                         #   available could exceed copies — no guard

        self.db.execute(
            "UPDATE loans SET returned = 'today' WHERE member_id = ? AND isbn = ?",
            [member_id, isbn]
        )


# ─── YOUR REDESIGN GOES BELOW ──────────────────────────────────────────────────

# Hint: start by asking these questions before writing any code:
#   - What invariants exist in this system? Who should own them?
#   - How many different "reasons to change" does Library have?
#   - What does Library depend on that might need to change (e.g. database)?
#   - What abstraction would let you test borrowing without a real database?

# class Book:
#     """Single responsibility: ..."""
#     pass

# class BookRepository(ABC):
#     """Single responsibility: ..."""
#     pass

# ... and so on


# ── Stub ──────────────────────────────────────────────────────────────────────

class DatabaseConnection:
    def execute(self, query: str, params: list = None): pass
