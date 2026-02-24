def main():
    # --- Predefined expense categories for easy selection ---
    categories = {
        1: "Sacks",
        2: "Lunch",
        3: "Breakfast",
        4: "Supper",
        5: "Utilities"
    }

    print("=" * 40)
    print("   Personal Financial Assistant")
    print("=" * 40)

    # --- Step 1: Get the user's budget ---
    while True:
        try:
            budget = float(input("\nEnter your budget for this period: "))
            if budget <= 0:
                print("Budget must be greater than zero. Try again.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    expenses = []      
    total_spent = 0.0   

    # --- Step 2: Show available categories and log transactions ---
    print("\n--- Expense Categories ---")
    for number, name in categories.items():
        print(f"  {number}. {name}")

    print("\nStart entering your expenses. Type '0' number to exit.\n")

    while True:
        print("Select a category:")
        for number, name in categories.items():
            print(f"  {number}. {name}")

        try:
            choice = int(input("Enter category number (0 to finish): "))
        except ValueError:
            print("Please enter a valid number.\n")
            continue

        if choice == 0:
            break

        # Validate the category choice
        if choice not in categories:
            print("Invalid category. Please choose a number from the list.\n")
            continue

        category_name = categories[choice]

        description = input(f"Enter a short description for '{category_name}' (e.g. 'Bought posho'): ")

        # --- Step 3: Get expense amount (must be greater than zero) ---
        try:
            amount = float(input(f"Enter amount spent on {category_name}: "))
            if amount <= 0:
                print("Expense amount must be greater than zero. Entry skipped.\n")
                continue
        except ValueError:
            print("Invalid amount. Please enter a number.\n")
            continue

        # (category, description, amount)
        expenses.append((category_name, description, amount))
        total_spent += amount

        # --- Step 4: Real-time balance check after each entry ---
        if total_spent > budget:
            print(f"⚠️  Warning: You are OVER budget by {total_spent - budget:.2f}!\n")
        else:
            remaining = budget - total_spent
            print(f"✅  Remaining balance: {remaining:.2f}\n")

    # --- Step 5: Print the final financial summary ---
    print("\n" + "=" * 40)
    print("        Financial Summary")
    print("=" * 40)
    print(f"Initial Budget : {budget:.2f}")
    print(f"Total Spent    : {total_spent:.2f}")

    if total_spent > budget:
        print(f"Deficit        : {total_spent - budget:.2f}  ⚠️")
    else:
        print(f"Balance Left   : {budget - total_spent:.2f}  ✅")

    # Print a numbered log of all transactions
    print("\n--- Transaction Log ---")
    if not expenses:
        print("No expenses were recorded.")
    else:
        for i, (category, description, amount) in enumerate(expenses, start=1):
            print(f"  {i}. [{category}] {description} - {amount:.2f}")

    print("=" * 40)
    print("Thank you for using your Financial Assistant!")


if __name__ == "__main__":
    main()