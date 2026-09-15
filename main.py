import sqlite3
from datetime import datetime

DB_NAME = "expenses.db"

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_table():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0)
            )
        """)
        conn.commit()

def add_expense():
    category = input("Category: ").strip()
    description = input("Description: ").strip()
    amount_text = input("Amount (₹): ").strip()

    try:
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        print("Invalid amount. Please enter a positive number.")
        return

    date = input("Date (YYYY-MM-DD) [press Enter for today]: ").strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format.")
        return

    with connect_db() as conn:
        conn.execute(
            "INSERT INTO expenses(date, category, description, amount) VALUES (?, ?, ?, ?)",
            (date, category, description, amount)
        )
        conn.commit()
    print("Expense added successfully.")

def view_expenses():
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT id, date, category, description, amount "
            "FROM expenses ORDER BY date DESC, id DESC"
        ).fetchall()

    if not rows:
        print("No expenses found.")
        return

    print("\nID | Date       | Category     | Description              | Amount")
    print("-" * 75)
    for row in rows:
        print(f"{row[0]:<2} | {row[1]:<10} | {row[2]:<12} | "
              f"{row[3][:24]:<24} | ₹{row[4]:.2f}")

def delete_expense():
    try:
        expense_id = int(input("Enter expense ID to delete: "))
    except ValueError:
        print("Invalid ID.")
        return

    with connect_db() as conn:
        cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()

    if cursor.rowcount:
        print("Expense deleted successfully.")
    else:
        print("Expense ID not found.")

def total_expenses():
    with connect_db() as conn:
        total = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses"
        ).fetchone()[0]
    print(f"Total expenses: ₹{total:.2f}")

def category_summary():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """).fetchall()

    if not rows:
        print("No expenses found.")
        return

    print("\nCategory Summary")
    print("-" * 35)
    for category, amount in rows:
        print(f"{category:<20} ₹{amount:.2f}")

def monthly_summary():
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT substr(date, 1, 7) AS month, SUM(amount)
            FROM expenses
            GROUP BY month
            ORDER BY month DESC
        """).fetchall()

    if not rows:
        print("No expenses found.")
        return

    print("\nMonthly Summary")
    print("-" * 35)
    for month, amount in rows:
        print(f"{month:<15} ₹{amount:.2f}")

def search_expenses():
    keyword = input("Search category/description: ").strip()
    with connect_db() as conn:
        rows = conn.execute("""
            SELECT id, date, category, description, amount
            FROM expenses
            WHERE category LIKE ? OR description LIKE ?
            ORDER BY date DESC
        """, (f"%{keyword}%", f"%{keyword}%")).fetchall()

    if not rows:
        print("No matching expenses found.")
        return

    for row in rows:
        print(f"ID:{row[0]} | {row[1]} | {row[2]} | {row[3]} | ₹{row[4]:.2f}")

def main():
    create_table()

    while True:
        print("""
========== EXPENSE TRACKER ==========
1. Add Expense
2. View All Expenses
3. Delete Expense
4. Show Total Expenses
5. Category Summary
6. Monthly Summary
7. Search Expenses
8. Exit
======================================
""")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            delete_expense()
        elif choice == "4":
            total_expenses()
        elif choice == "5":
            category_summary()
        elif choice == "6":
            monthly_summary()
        elif choice == "7":
            search_expenses()
        elif choice == "8":
            print("Thank you for using Expense Tracker!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
