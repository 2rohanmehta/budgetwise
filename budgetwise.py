import os
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BudgetWiseApp:
    def __init__(self, master):
        self.master = master
        self.master.title("BudgetWise - Personal Budgeting App")
        self.master.geometry("1350x780")
        self.bg_color = "#232733"
        self.card_color = "#2b3040"
        self.accent_color = "#4fa3ff"
        self.text_primary = "#f5f5f5"
        self.text_secondary = "#d0d0d0"
        self.warning_color = "#ffb74d"
        self.master.configure(bg=self.bg_color)
        self.transactions_file = "budgetwise_transactions.csv"
        self.settings_file = "budgetwise_settings.json"
        self.transactions = self.load_transactions()
        self.settings = self.load_settings()
        self.current_chart_type = "expenses_by_category"
        self.create_widgets()
        self.refresh_dashboard()

    def load_transactions(self):
        if os.path.exists(self.transactions_file):
            df = pd.read_csv(self.transactions_file)
            if not df.empty and "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])
                return df
        columns = ["date", "type", "category", "description", "amount"]
        return pd.DataFrame(columns=columns)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "monthly_savings_goal" in data:
                        return data
            except Exception:
                pass
        return {"monthly_savings_goal": 0.0}

    def save_transactions(self):
        df = self.transactions.copy()
        if not df.empty:
            df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        df.to_csv(self.transactions_file, index=False)

    def save_settings(self):
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f)

    def create_widgets(self):
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background=self.bg_color)
        style.configure("Card.TFrame", background=self.card_color, relief="ridge")
        style.configure("Dashboard.TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_secondary, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=self.bg_color, foreground=self.text_primary, font=("Segoe UI", 14, "bold"))
        style.configure("Value.TLabel", background=self.bg_color, foreground=self.text_primary, font=("Segoe UI", 11, "bold"))
        style.configure("Hint.TLabel", background=self.bg_color, foreground=self.text_secondary, font=("Segoe UI", 9))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Accent.TButton", background=[("!disabled", self.accent_color), ("pressed", "#3476b5"), ("active", "#5fb0ff")], foreground=[("!disabled", "#ffffff")])
        style.configure("TButton", padding=5, font=("Segoe UI", 10))
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#2f3440", foreground=self.text_secondary, padding=(10, 6))
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)], foreground=[("selected", "#ffffff")])
        style.configure("Goal.Horizontal.TProgressbar", troughcolor="#171a22", bordercolor="#171a22", background="#66bb6a")
        style.configure("Treeview", background=self.card_color, foreground=self.text_primary, fieldbackground=self.card_color, rowheight=22, bordercolor=self.bg_color, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#383f52", foreground=self.text_primary, font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", self.accent_color)], foreground=[("selected", "#ffffff")])
        style.configure("TCombobox", fieldbackground=self.card_color, background=self.card_color, foreground=self.text_primary)
        notebook = ttk.Notebook(self.master)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.dashboard_frame = ttk.Frame(notebook, style="Dashboard.TFrame", padding=10)
        self.add_frame = ttk.Frame(notebook, style="Dashboard.TFrame", padding=10)
        self.settings_frame = ttk.Frame(notebook, style="Dashboard.TFrame", padding=10)
        notebook.add(self.dashboard_frame, text="Dashboard")
        notebook.add(self.add_frame, text="Add Transaction")
        notebook.add(self.settings_frame, text="Settings")
        self.create_dashboard_tab()
        self.create_add_tab()
        self.create_settings_tab()

    def create_dashboard_tab(self):
        top_frame = ttk.Frame(self.dashboard_frame, style="Dashboard.TFrame")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        summary_card = ttk.Frame(top_frame, style="Card.TFrame", padding=10)
        summary_card.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 10))
        self.total_income_var = tk.StringVar()
        self.total_expenses_var = tk.StringVar()
        self.net_balance_var = tk.StringVar()
        self.savings_goal_var = tk.StringVar()
        self.remaining_goal_var = tk.StringVar()
        ttk.Label(summary_card, textvariable=self.total_income_var, style="Value.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 20), pady=2)
        ttk.Label(summary_card, textvariable=self.total_expenses_var, style="Value.TLabel").grid(row=0, column=1, sticky="w", padx=(0, 20), pady=2)
        ttk.Label(summary_card, textvariable=self.net_balance_var, style="Value.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 20), pady=2)
        ttk.Label(summary_card, textvariable=self.savings_goal_var, style="Value.TLabel").grid(row=1, column=0, sticky="w", padx=(0, 20), pady=2)
        ttk.Label(summary_card, textvariable=self.remaining_goal_var, style="Value.TLabel").grid(row=1, column=1, sticky="w", padx=(0, 20), pady=2)
        summary_card.columnconfigure(0, weight=1)
        summary_card.columnconfigure(1, weight=1)
        summary_card.columnconfigure(2, weight=1)
        progress_card = ttk.Frame(top_frame, style="Card.TFrame", padding=10)
        progress_card.pack(fill=tk.BOTH, side=tk.RIGHT)
        ttk.Label(progress_card, text="Savings Goal Progress (Current Month)", background=self.card_color, foreground=self.text_primary, font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_card, variable=self.progress_var, maximum=100, style="Goal.Horizontal.TProgressbar")
        self.progress_bar.pack(fill=tk.X, pady=(8, 4), ipady=6)
        self.progress_text_var = tk.StringVar()
        ttk.Label(progress_card, textvariable=self.progress_text_var, background=self.card_color, foreground=self.text_secondary, font=("Segoe UI", 10)).pack(anchor="w")
        table_chart_frame = ttk.Frame(self.dashboard_frame, style="Dashboard.TFrame")
        table_chart_frame.pack(fill=tk.BOTH, expand=True)
        table_card = ttk.Frame(table_chart_frame, style="Card.TFrame", padding=8)
        table_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        ttk.Label(table_card, text="Current Month Transactions", background=self.card_color, foreground=self.text_primary, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        columns = ("date", "type", "category", "description", "amount")
        self.transactions_tree = ttk.Treeview(table_card, columns=columns, show="headings", height=15)
        self.transactions_tree.heading("date", text="Date")
        self.transactions_tree.heading("type", text="Type")
        self.transactions_tree.heading("category", text="Category")
        self.transactions_tree.heading("description", text="Description")
        self.transactions_tree.heading("amount", text="Amount")
        self.transactions_tree.column("date", width=90, anchor="center")
        self.transactions_tree.column("type", width=80, anchor="center")
        self.transactions_tree.column("category", width=120, anchor="w")
        self.transactions_tree.column("description", width=210, anchor="w")
        self.transactions_tree.column("amount", width=90, anchor="e")
        self.transactions_tree.tag_configure("evenrow", background="#33394a")
        self.transactions_tree.tag_configure("oddrow", background=self.card_color)
        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=vsb.set)
        self.transactions_tree.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=1, column=1, sticky="ns")
        control_frame = ttk.Frame(table_card, style="Card.TFrame")
        control_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(6, 0))
        delete_button = ttk.Button(control_frame, text="Delete Selected", style="Accent.TButton", command=self.delete_selected_transaction)
        delete_button.pack(side=tk.LEFT)
        table_card.rowconfigure(1, weight=1)
        table_card.columnconfigure(0, weight=1)
        chart_card = ttk.Frame(table_chart_frame, style="Card.TFrame", padding=8)
        chart_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        header_row = ttk.Frame(chart_card, style="Card.TFrame")
        header_row.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(header_row, text="Spending Insights", background=self.card_color, foreground=self.text_primary, font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        chart_buttons_frame = ttk.Frame(chart_card, style="Card.TFrame")
        chart_buttons_frame.pack(fill=tk.X, pady=(0, 5))
        expenses_chart_button = ttk.Button(chart_buttons_frame, text="Spending by Category", style="Accent.TButton", command=self.show_expenses_by_category_chart)
        income_vs_expense_button = ttk.Button(chart_buttons_frame, text="Income vs Expenses", command=self.show_income_vs_expense_chart)
        expenses_chart_button.pack(side=tk.LEFT, padx=(0, 6))
        income_vs_expense_button.pack(side=tk.LEFT)
        self.figure = Figure(figsize=(4.5, 3.2), dpi=100)
        self.figure.patch.set_facecolor(self.card_color)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=chart_card)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    def create_add_tab(self):
        container = ttk.Frame(self.add_frame, style="Dashboard.TFrame")
        container.pack(fill=tk.BOTH, expand=True)
        form_card = ttk.Frame(container, style="Card.TFrame", padding=12)
        form_card.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(form_card, text="Add New Transaction", background=self.card_color, foreground=self.text_primary, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(form_card, text="Date (YYYY-MM-DD):", background=self.card_color, foreground=self.text_secondary).grid(row=1, column=0, sticky="w", pady=4)
        ttk.Label(form_card, text="Type:", background=self.card_color, foreground=self.text_secondary).grid(row=2, column=0, sticky="w", pady=4)
        ttk.Label(form_card, text="Category:", background=self.card_color, foreground=self.text_secondary).grid(row=3, column=0, sticky="w", pady=4)
        ttk.Label(form_card, text="Description:", background=self.card_color, foreground=self.text_secondary).grid(row=4, column=0, sticky="w", pady=4)
        ttk.Label(form_card, text="Amount:", background=self.card_color, foreground=self.text_secondary).grid(row=5, column=0, sticky="w", pady=4)
        self.date_entry = ttk.Entry(form_card)
        self.date_entry.grid(row=1, column=1, sticky="we", pady=4)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_var = tk.StringVar(value="Expense")
        type_combo = ttk.Combobox(form_card, textvariable=self.type_var, values=["Income", "Expense"], state="readonly")
        type_combo.grid(row=2, column=1, sticky="we", pady=4)
        self.category_var = tk.StringVar()
        self.category_placeholder = "Select category..."
        default_categories = [
            self.category_placeholder,
            "Salary",
            "Scholarship",
            "Food",
            "Rent",
            "Utilities",
            "Transport",
            "Entertainment",
            "Savings",
            "Other",
        ]
        self.category_combo = ttk.Combobox(form_card, textvariable=self.category_var, values=default_categories, state="readonly")
        self.category_combo.grid(row=3, column=1, sticky="we", pady=4)
        self.category_combo.set(self.category_placeholder)
        self.description_entry = ttk.Entry(form_card)
        self.description_entry.grid(row=4, column=1, sticky="we", pady=4)
        self.amount_entry = ttk.Entry(form_card)
        self.amount_entry.grid(row=5, column=1, sticky="we", pady=4)
        form_card.columnconfigure(1, weight=1)
        hint = ttk.Label(form_card, text="Tip: Choose Income for money you receive and Expense for money you spend.", background=self.card_color, foreground=self.text_secondary, font=("Segoe UI", 9, "italic"))
        hint.grid(row=6, column=0, columnspan=2, sticky="w", pady=(4, 0))
        button_frame = ttk.Frame(container, style="Dashboard.TFrame")
        button_frame.pack(fill=tk.X, pady=(6, 0))
        add_button = ttk.Button(button_frame, text="Add Transaction", style="Accent.TButton", command=self.add_transaction)
        add_button.pack(side=tk.LEFT)
        clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_transaction_form)
        clear_button.pack(side=tk.LEFT, padx=(8, 0))

    def create_settings_tab(self):
        settings_card = ttk.Frame(self.settings_frame, style="Card.TFrame", padding=12)
        settings_card.pack(fill=tk.X)
        ttk.Label(settings_card, text="Savings Goal Settings", background=self.card_color, foreground=self.text_primary, font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(settings_card, text="Monthly Savings Goal ($):", background=self.card_color, foreground=self.text_secondary).grid(row=1, column=0, sticky="w", pady=4)
        self.goal_entry_var = tk.StringVar()
        current_goal = self.settings.get("monthly_savings_goal", 0.0)
        if isinstance(current_goal, (int, float)):
            self.goal_entry_var.set(f"{current_goal:.2f}")
        else:
            self.goal_entry_var.set("0.00")
        goal_entry = ttk.Entry(settings_card, textvariable=self.goal_entry_var)
        goal_entry.grid(row=1, column=1, sticky="we", pady=4)
        settings_card.columnconfigure(1, weight=1)
        save_button = ttk.Button(settings_card, text="Save Goal", style="Accent.TButton", command=self.save_goal_from_entry)
        save_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="w")
        info_text = (
            "BudgetWise compares your total income and expenses each month against this savings goal.\n"
            "If your spending makes it impossible to reach the goal, you will see a gentle budget alert."
        )
        info_label = ttk.Label(self.settings_frame, text=info_text, style="Hint.TLabel", wraplength=650, justify="left")
        info_label.pack(fill=tk.X, pady=(10, 0))

    def add_transaction(self):
        date_str = self.date_entry.get().strip()
        type_value = self.type_var.get().strip()
        category_value = self.category_var.get().strip()
        if category_value == self.category_placeholder or not category_value:
            category_value = "Uncategorized"
        description_value = self.description_entry.get().strip()
        amount_str = self.amount_entry.get().strip()
        if not date_str or not type_value or not amount_str:
            messagebox.showerror("Missing Information", "Date, type, and amount are required.")
            return
        try:
            date_value = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format.")
            return
        try:
            amount_value = float(amount_str)
        except ValueError:
            messagebox.showerror("Invalid Amount", "Amount must be a valid number.")
            return
        if amount_value <= 0:
            messagebox.showerror("Invalid Amount", "Amount must be greater than zero.")
            return
        new_row = {
            "date": date_value,
            "type": type_value,
            "category": category_value,
            "description": description_value,
            "amount": amount_value,
        }
        self.transactions = pd.concat([self.transactions, pd.DataFrame([new_row])], ignore_index=True)
        self.save_transactions()
        self.refresh_dashboard()
        self.check_budget_alert(date_value)
        self.clear_transaction_form()
        messagebox.showinfo("Success", "Transaction added successfully.")

    def clear_transaction_form(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.type_var.set("Expense")
        self.category_combo.set(self.category_placeholder)
        self.description_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def save_goal_from_entry(self):
        goal_str = self.goal_entry_var.get().strip()
        try:
            goal_value = float(goal_str)
        except ValueError:
            messagebox.showerror("Invalid Goal", "Savings goal must be a valid number.")
            return
        if goal_value < 0:
            messagebox.showerror("Invalid Goal", "Savings goal cannot be negative.")
            return
        self.settings["monthly_savings_goal"] = goal_value
        self.save_settings()
        self.refresh_dashboard()
        messagebox.showinfo("Goal Saved", "Monthly savings goal updated.")

    def get_current_month_data(self):
        if self.transactions.empty:
            return self.transactions
        now = datetime.now()
        mask = (self.transactions["date"].dt.year == now.year) & (self.transactions["date"].dt.month == now.month)
        return self.transactions.loc[mask]

    def refresh_dashboard(self):
        month_data = self.get_current_month_data()
        total_income = 0.0
        total_expenses = 0.0
        if not month_data.empty:
            income_data = month_data[month_data["type"] == "Income"]
            expense_data = month_data[month_data["type"] == "Expense"]
            total_income = income_data["amount"].sum()
            total_expenses = expense_data["amount"].sum()
        net_balance = total_income - total_expenses
        savings_goal = float(self.settings.get("monthly_savings_goal", 0.0))
        remaining_to_goal = max(savings_goal - max(net_balance, 0.0), 0.0)
        self.total_income_var.set(f"Total Income (This Month): ${total_income:,.2f}")
        self.total_expenses_var.set(f"Total Expenses (This Month): ${total_expenses:,.2f}")
        self.net_balance_var.set(f"Net Balance (This Month): ${net_balance:,.2f}")
        self.savings_goal_var.set(f"Savings Goal: ${savings_goal:,.2f}")
        self.remaining_goal_var.set(f"Remaining To Goal: ${remaining_to_goal:,.2f}")
        progress = 0.0
        if savings_goal > 0:
            progress = max(min((max(net_balance, 0.0) / savings_goal) * 100.0, 100.0), 0.0)
        self.progress_var.set(progress)
        if savings_goal <= 0:
            self.progress_text_var.set("Set a monthly savings goal to track your progress.")
        else:
            self.progress_text_var.set(f"Progress: {progress:.1f}% of your ${savings_goal:,.2f} goal")
        for item in self.transactions_tree.get_children():
            self.transactions_tree.delete(item)
        if not month_data.empty:
            sorted_data = month_data.sort_values("date")
            for index, (_, row) in enumerate(sorted_data.iterrows()):
                date_str = row["date"].strftime("%Y-%m-%d")
                amount_str = f"${row['amount']:,.2f}"
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.transactions_tree.insert(
                    "",
                    tk.END,
                    values=(date_str, row["type"], row["category"], row["description"], amount_str),
                    tags=(tag,),
                )
        if self.current_chart_type == "expenses_by_category":
            self.show_expenses_by_category_chart()
        else:
            self.show_income_vs_expense_chart()

    def style_axes(self, ax):
        ax.set_facecolor(self.card_color)
        for spine in ax.spines.values():
            spine.set_color(self.text_secondary)
        ax.tick_params(colors=self.text_secondary)
        ax.title.set_color(self.text_primary)
        ax.yaxis.label.set_color(self.text_secondary)
        ax.xaxis.label.set_color(self.text_secondary)

    def show_expenses_by_category_chart(self):
        self.current_chart_type = "expenses_by_category"
        month_data = self.get_current_month_data()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if month_data.empty:
            ax.text(0.5, 0.5, "No data for current month", ha="center", va="center", color=self.text_secondary, fontsize=11)
        else:
            expenses = month_data[month_data["type"] == "Expense"]
            if expenses.empty:
                ax.text(0.5, 0.5, "No expenses for current month", ha="center", va="center", color=self.text_secondary, fontsize=11)
            else:
                grouped = expenses.groupby("category")["amount"].sum().sort_values(ascending=False)
                categories = grouped.index.tolist()
                amounts = grouped.values.tolist()
                bars = ax.bar(categories, amounts)
                for bar in bars:
                    bar.set_color(self.accent_color)
                ax.set_title("Spending by Category (This Month)")
                ax.set_ylabel("Amount ($)")
                ax.set_xticklabels(categories, rotation=35, ha="right")
        self.style_axes(ax)
        self.figure.tight_layout()
        self.chart_canvas.draw()

    def show_income_vs_expense_chart(self):
        self.current_chart_type = "income_vs_expense"
        month_data = self.get_current_month_data()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if month_data.empty:
            ax.text(0.5, 0.5, "No data for current month", ha="center", va="center", color=self.text_secondary, fontsize=11)
        else:
            income_total = month_data[month_data["type"] == "Income"]["amount"].sum()
            expense_total = month_data[month_data["type"] == "Expense"]["amount"].sum()
            labels = ["Income", "Expenses"]
            values = [income_total, expense_total]
            colors = ["#66bb6a", "#ef5350"]
            bars = ax.bar(labels, values)
            for bar, c in zip(bars, colors):
                bar.set_color(c)
            ax.set_title("Income vs Expenses (This Month)")
            ax.set_ylabel("Amount ($)")
        self.style_axes(ax)
        self.figure.tight_layout()
        self.chart_canvas.draw()

    def check_budget_alert(self, date_value):
        month_data = self.transactions.copy()
        if month_data.empty:
            return
        mask = (month_data["date"].dt.year == date_value.year) & (month_data["date"].dt.month == date_value.month)
        month_data = month_data.loc[mask]
        income_total = month_data[month_data["type"] == "Income"]["amount"].sum()
        expense_total = month_data[month_data["type"] == "Expense"]["amount"].sum()
        savings_goal = float(self.settings.get("monthly_savings_goal", 0.0))
        if income_total <= 0:
            return
        budget_limit = max(income_total - savings_goal, 0.0)
        if expense_total > budget_limit and budget_limit > 0:
            messagebox.showwarning(
                "Budget Alert",
                "Your expenses for this month have exceeded the recommended budget to meet your savings goal.",
            )

    def delete_selected_transaction(self):
        selected_items = self.transactions_tree.selection()
        if not selected_items:
            messagebox.showerror("No Selection", "Please select at least one transaction to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected transaction(s)?")
        if not confirm:
            return
        for item in selected_items:
            values = self.transactions_tree.item(item, "values")
            if len(values) != 5:
                continue
            date_str, type_value, category_value, description_value, amount_str = values
            try:
                date_value = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            amount_clean = amount_str.replace("$", "").replace(",", "")
            try:
                amount_value = float(amount_clean)
            except ValueError:
                continue
            mask = (
                (self.transactions["date"] == date_value)
                & (self.transactions["type"] == type_value)
                & (self.transactions["category"] == category_value)
                & (self.transactions["description"] == description_value)
                & (self.transactions["amount"] == amount_value)
            )
            self.transactions = self.transactions.loc[~mask]
        self.transactions.reset_index(drop=True, inplace=True)
        self.save_transactions()
        self.refresh_dashboard()
        messagebox.showinfo("Deleted", "Selected transaction(s) deleted.")


def main():
    root = tk.Tk()
    app = BudgetWiseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
