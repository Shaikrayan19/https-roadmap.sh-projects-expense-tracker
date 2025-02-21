#!/usr/bin/env python3

import argparse
import json
import os
from datetime import datetime
from tabulate import tabulate

# Constants
DATA_FILE = "expenses.json"
CATEGORIES = [
    "Food", "Transportation", "Housing", "Utilities", 
    "Entertainment", "Shopping", "Healthcare", "Other"
]

def load_expenses():
    """Load expenses from JSON file"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_expenses(expenses):
    """Save expenses to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(expenses, f, indent=2)

def get_next_id(expenses):
    """Get next available ID for new expense"""
    if not expenses:
        return 1
    return max(expense['id'] for expense in expenses) + 1

def validate_amount(amount):
    """Validate expense amount"""
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount
    except ValueError:
        raise ValueError("Invalid amount")

def validate_category(category):
    """Validate expense category"""
    if category not in CATEGORIES:
        categories_str = ", ".join(CATEGORIES)
        raise ValueError(f"Invalid category. Available categories: {categories_str}")
    return category

def add_expense(description, amount, category):
    """Add a new expense"""
    try:
        amount = validate_amount(amount)
        category = validate_category(category)
        expenses = load_expenses()
        new_expense = {
            'id': get_next_id(expenses),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': description,
            'amount': amount,
            'category': category
        }
        expenses.append(new_expense)
        save_expenses(expenses)
        print(f"Expense added successfully (ID: {new_expense['id']})")
    except ValueError as e:
        print(f"Error: {str(e)}")

def update_expense(expense_id, description=None, amount=None, category=None):
    """Update an existing expense"""
    try:
        expenses = load_expenses()
        for expense in expenses:
            if expense['id'] == expense_id:
                if description is not None:
                    expense['description'] = description
                if amount is not None:
                    expense['amount'] = validate_amount(amount)
                if category is not None:
                    expense['category'] = validate_category(category)
                save_expenses(expenses)
                print(f"Expense updated successfully (ID: {expense_id})")
                return
        print(f"Error: No expense found with ID {expense_id}")
    except ValueError as e:
        print(f"Error: {str(e)}")

def list_expenses(category=None):
    """List all expenses in tabular format, optionally filtered by category"""
    expenses = load_expenses()
    if not expenses:
        print("No expenses found")
        return

    if category:
        try:
            validate_category(category)
            expenses = [exp for exp in expenses if exp['category'] == category]
            if not expenses:
                print(f"No expenses found in category: {category}")
                return
        except ValueError as e:
            print(f"Error: {str(e)}")
            return

    # Prepare table data
    headers = ["ID", "Date", "Category", "Description", "Amount"]
    rows = [[exp['id'], exp['date'], exp['category'], exp['description'], f"${exp['amount']:.2f}"] 
            for exp in expenses]

    print(tabulate(rows, headers=headers, tablefmt="simple"))

def get_summary(month=None, category=None):
    """Get expense summary, optionally filtered by month and/or category"""
    expenses = load_expenses()
    if not expenses:
        print("No expenses found")
        return

    # Filter by category if specified
    if category:
        try:
            validate_category(category)
            expenses = [exp for exp in expenses if exp['category'] == category]
            if not expenses:
                print(f"No expenses found in category: {category}")
                return
        except ValueError as e:
            print(f"Error: {str(e)}")
            return

    # Filter by month if specified
    if month:
        try:
            month = int(month)
            if not 1 <= month <= 12:
                raise ValueError
            current_year = datetime.now().year
            expenses = [exp for exp in expenses 
                       if datetime.strptime(exp['date'], '%Y-%m-%d').month == month
                       and datetime.strptime(exp['date'], '%Y-%m-%d').year == current_year]
        except ValueError:
            print("Error: Invalid month")
            return

    # Calculate totals
    total = sum(exp['amount'] for exp in expenses)

    # Show summary based on filters
    if month and category:
        print(f"Total expenses for {datetime.strptime(str(month), '%m').strftime('%B')} in category {category}: ${total:.2f}")
    elif month:
        print(f"Total expenses for {datetime.strptime(str(month), '%m').strftime('%B')}: ${total:.2f}")
    elif category:
        print(f"Total expenses in category {category}: ${total:.2f}")
    else:
        print(f"Total expenses: ${total:.2f}")

        # Show breakdown by category
        print("\nBreakdown by category:")
        for cat in CATEGORIES:
            cat_total = sum(exp['amount'] for exp in expenses if exp['category'] == cat)
            if cat_total > 0:
                print(f"{cat}: ${cat_total:.2f}")

def delete_expense(expense_id):
    """Delete an expense by ID"""
    expenses = load_expenses()
    initial_length = len(expenses)
    expenses = [exp for exp in expenses if exp['id'] != expense_id]

    if len(expenses) == initial_length:
        print(f"Error: No expense found with ID {expense_id}")
        return

    save_expenses(expenses)
    print("Expense deleted successfully")

def main():
    parser = argparse.ArgumentParser(description='Expense Tracker')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new expense')
    add_parser.add_argument('--description', required=True, help='Expense description')
    add_parser.add_argument('--amount', required=True, help='Expense amount')
    add_parser.add_argument('--category', required=True, help=f'Expense category ({", ".join(CATEGORIES)})')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update an existing expense')
    update_parser.add_argument('--id', type=int, required=True, help='Expense ID to update')
    update_parser.add_argument('--description', help='New expense description')
    update_parser.add_argument('--amount', help='New expense amount')
    update_parser.add_argument('--category', help=f'New expense category ({", ".join(CATEGORIES)})')

    # List command
    list_parser = subparsers.add_parser('list', help='List all expenses')
    list_parser.add_argument('--category', help=f'Filter by category ({", ".join(CATEGORIES)})')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete an expense')
    delete_parser.add_argument('--id', type=int, required=True, help='Expense ID to delete')

    # Summary command
    summary_parser = subparsers.add_parser('summary', help='Show expense summary')
    summary_parser.add_argument('--month', type=int, help='Month number (1-12)')
    summary_parser.add_argument('--category', help=f'Filter by category ({", ".join(CATEGORIES)})')

    args = parser.parse_args()

    if args.command == 'add':
        add_expense(args.description, args.amount, args.category)
    elif args.command == 'update':
        if all(arg is None for arg in [args.description, args.amount, args.category]):
            print("Error: At least one of --description, --amount, or --category must be provided")
            return
        update_expense(args.id, args.description, args.amount, args.category)
    elif args.command == 'list':
        list_expenses(args.category)
    elif args.command == 'delete':
        delete_expense(args.id)
    elif args.command == 'summary':
        get_summary(args.month, args.category)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
