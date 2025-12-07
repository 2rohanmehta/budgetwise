# BudgetWise — Midnight Finance Edition

A personal budget tracking desktop app built with Python and Tkinter. Track income and expenses, visualize spending patterns, and monitor progress toward your savings goals.

![Python](https://img.shields.io/badge/Python-3.8+-blue)

## Features

- Add, edit, and delete transactions
- View monthly income, expenses, and net balance
- Set and track monthly savings goals with progress bar
- Visualize spending by category or income vs expenses
- Data stored locally in SQLite database

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation

### Windows

1. **Open PowerShell or Command Prompt**

2. **Navigate to the project folder**

   ```powershell
   cd C:\path\to\your\project
   ```

3. **Install required modules**

   ```powershell
   pip install pandas matplotlib sqlalchemy
   ```

4. **Run the app**
   ```powershell
   python budgetwise.py
   ```

### Mac

1. **Open Terminal**

2. **Navigate to the project folder**

   ```bash
   cd /path/to/your/project
   ```

3. **Install required modules**

   ```bash
   pip3 install pandas matplotlib sqlalchemy
   ```

4. **Run the app**
   ```bash
   python3 budgetwise.py
   ```

> **Note:** On Mac, use `python3` and `pip3` instead of `python` and `pip` to ensure you're using Python 3.

## Dependencies

| Module       | Purpose                              |
| ------------ | ------------------------------------ |
| `tkinter`    | GUI framework (included with Python) |
| `pandas`     | Data manipulation and analysis       |
| `matplotlib` | Charts and visualizations            |
| `sqlalchemy` | Database ORM for SQLite              |

## Usage

1. **Dashboard** — View your current month's transactions, summary stats, and charts
2. **Add Transaction** — Enter new income or expenses with date, category, and amount
3. **Settings** — Set your monthly savings goal

### Setting a Monthly Savings Goal

1. Click the **Settings** tab
2. Enter your desired savings goal amount in the text field
3. Click **Save Goal**
4. Your progress will now show on the Dashboard with a progress bar tracking how close you are to your goal based on your net income (income minus expenses) for the current month

### Editing a Transaction

1. Select a row in the dashboard table
2. Click "Edit Selected"
3. Modify the fields and click "Save Changes"

### Deleting a Transaction

1. Select a row in the dashboard table
2. Click "Delete Selected"

## Data Storage

All data is stored locally in `budgetwise.db` (SQLite database) in the same folder as the app. No internet connection required.
