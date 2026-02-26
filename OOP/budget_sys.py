import sys

class Expense:
    """
    Data Class to represent a single financial transaction.
    """
    def __init__(self, category, description, amount):
        self.category = category
        self.description = description
        self.amount = amount

    def __str__(self):
        """Returns a formatted string for the transaction log."""
        return f"[{self.category}] {self.description} - {self.amount:.2f}"


class BudgetTracker:
    """
    The 'Engine' of the application. 
    Manages the budget logic, category definitions, and expense collection.
    """
    # --- Constants to replace 'Magic Numbers' ---
    EXIT_CODE = 0
    MIN_BUDGET = 1
    
    # Predefined categories stored within the class context
    CATEGORIES = {
        1: "Sacks",
        2: "Lunch",
        3: "Breakfast",
        4: "Supper",
        5: "Utilities"
    }

    def __init__(self, budget):
        self.budget = budget
        self.expenses = []

    def get_total_spent(self):
        """Calculates total spending dynamically from the list of objects."""
        return sum(exp.amount for exp in self.expenses)

    def get_remaining_balance(self):
        """Calculates the difference between budget and spending."""
        return self.budget - self.get_total_spent()

    def add_expense(self, category_index, description, amount):
        """Creates an Expense object and adds it to the internal list."""
        category_name = self.CATEGORIES.get(category_index, "Unknown")
        new_expense = Expense(category_name, description, amount)
        self.expenses.append(new_expense)
        return new_expense


def main():
    """
    The 'User Interface' layer.
    Handles all print() and input() calls, delegating logic to the BudgetTracker.
    """
    print("=" * 40)
    print("    Personal Financial Assistant (OOP)")
    print("=" * 40)

    while True:
        try:
            user_budget = float(input("\nEnter your budget for this period: "))
            if user_budget < BudgetTracker.MIN_BUDGET:
                print(f"Budget must be at least {BudgetTracker.MIN_BUDGET}. Try again.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    # Create the tracker instance (The Object)
    tracker = BudgetTracker(user_budget)

    # --- Transaction Loop ---
    print(f"\nStart entering expenses. Type '{BudgetTracker.EXIT_CODE}' to finish.")
    
    while True:
        print("\n--- Categories ---")
        for num, name in tracker.CATEGORIES.items():
            print(f"  {num}. {name}")

        try:
            choice = int(input(f"Select category ({BudgetTracker.EXIT_CODE} to exit): "))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if choice == BudgetTracker.EXIT_CODE:
            break

        if choice not in tracker.CATEGORIES:
            print("Invalid choice. Please pick from the list.")
            continue

        description = input(f"Description for '{tracker.CATEGORIES[choice]}': ")

        try:
            amount = float(input(f"Amount spent: "))
            if amount <= 0:
                print("Amount must be positive. Entry skipped.")
                continue
        except ValueError:
            print("Invalid amount. Entry skipped.")
            continue

        # Use the tracker object to record the expense
        tracker.add_expense(choice, description, amount)

        # Real-time feedback using object methods
        current_balance = tracker.get_remaining_balance()
        if current_balance < 0:
            print(f"⚠️  Warning: Over budget by {abs(current_balance):.2f}!")
        else:
            print(f"✅  Remaining: {current_balance:.2f}")

    # --- Final Summary ---
    print("\n" + "=" * 40)
    print("          FINANCIAL SUMMARY")
    print("=" * 40)
    print(f"Initial Budget : {tracker.budget:.2f}")
    print(f"Total Spent    : {tracker.get_total_spent():.2f}")

    balance = tracker.get_remaining_balance()
    if balance < 0:
        print(f"Deficit        : {abs(balance):.2f} ⚠️")
    else:
        print(f"Balance Left   : {balance:.2f} ✅")

    print("\n--- Transaction Log ---")
    if not tracker.expenses:
        print("No records found.")
    else:
        # Loop through the list of Expense objects
        for i, exp in enumerate(tracker.expenses, 1):
            print(f"  {i}. {exp}") # Calls the __str__ method of Expense

    print("=" * 40)
    print("Stay financially savvy!")


if __name__ == "__main__":
    main()