import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, Text
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine("sqlite:///budgetwise.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    type = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(Text)
    amount = Column(Float, nullable=False)


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True)
    value = Column(String(200))


Base.metadata.create_all(bind=engine)


class BudgetWiseApp:
    def __init__(self, master):
        self.master = master
        self.master.title("BudgetWise — Midnight Finance Edition")
        self.master.geometry("1450x880")
        self.bg = "#0D1117"
        self.card = "#161B22"
        self.card2 = "#1D242D"
        self.navy = "#0A192F"
        self.accent = "#00C6D7"
        self.gold = "#F9D342"
        self.text = "#C9D1D9"
        self.master.configure(bg=self.bg)

        self.settings = self.load_settings()
        self.transactions_df = self.load_transactions_df()
        self.current_chart = "category"

        self.style_ui()
        self.build_ui()
        self.refresh_dashboard()

    def load_transactions_df(self):
        s = SessionLocal()
        rows = s.query(Transaction).all()
        s.close()
        if not rows:
            return pd.DataFrame(columns=["id", "date", "type", "category", "description", "amount"])
        df = pd.DataFrame(
            [
                {
                    "id": r.id,
                    "date": pd.to_datetime(r.date),
                    "type": r.type,
                    "category": r.category,
                    "description": r.description,
                    "amount": r.amount,
                }
                for r in rows
            ]
        )
        return df

    def load_settings(self):
        s = SessionLocal()
        row = s.query(Setting).filter_by(key="monthly_savings_goal").first()
        s.close()
        if row:
            return {"monthly_savings_goal": float(row.value)}
        return {"monthly_savings_goal": 0.0}

    def save_setting(self, key, value):
        s = SessionLocal()
        row = s.query(Setting).filter_by(key=key).first()
        if not row:
            row = Setting(key=key, value=str(value))
            s.add(row)
        else:
            row.value = str(value)
        s.commit()
        s.close()

    def style_ui(self):
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("Dark.TFrame", background=self.bg)
        st.configure("Card.TFrame", background=self.card, relief="flat")
        st.configure("Text.TLabel", background=self.bg, foreground=self.text, font=("Inter", 11))
        st.configure("Bold.TLabel", background=self.bg, foreground=self.gold, font=("Inter", 13, "bold"))
        st.configure("Accent.TButton", font=("Inter", 11, "bold"), padding=8,
                     background=self.accent, foreground="#000000", borderwidth=0)
        st.map("Accent.TButton",
               background=[("active", "#33DCEB"), ("pressed", "#0094A3")],
               foreground=[("active", "#000"), ("pressed", "#000")])
        st.configure("Treeview",
                     background=self.card2,
                     fieldbackground=self.card2,
                     foreground=self.text,
                     rowheight=28,
                     borderwidth=0,
                     font=("Inter", 10))
        st.configure("Treeview.Heading",
                     background=self.navy,
                     foreground=self.gold,
                     font=("Inter", 11, "bold"))
        st.configure("TNotebook", background=self.bg)
        st.configure("TNotebook.Tab",
                     background=self.card2,
                     foreground=self.text,
                     padding=(14, 8),
                     font=("Inter", 11, "bold"))
        st.configure(
                    "TProgressbar",
                    troughcolor="#0A0F14",
                    background="#009EAA",
                    lightcolor="#33DCEB",
                    darkcolor="#006A72",
                        )
        st.map("TNotebook.Tab",
               background=[("selected", self.accent)],
               foreground=[("selected", "#000")])

    def build_ui(self):
        nb = ttk.Notebook(self.master)
        nb.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)
        self.tab_dashboard = ttk.Frame(nb, style="Dark.TFrame")
        self.tab_add = ttk.Frame(nb, style="Dark.TFrame")
        self.tab_settings = ttk.Frame(nb, style="Dark.TFrame")
        nb.add(self.tab_dashboard, text="Dashboard")
        nb.add(self.tab_add, text="Add Transaction")
        nb.add(self.tab_settings, text="Settings")
        self.build_dashboard()
        self.build_add_transaction()
        self.build_settings_tab()

    def build_dashboard(self):
        top = ttk.Frame(self.tab_dashboard, style="Dark.TFrame")
        top.pack(fill=tk.X, pady=10)

        self.lbl_income = ttk.Label(top, style="Bold.TLabel")
        self.lbl_expenses = ttk.Label(top, style="Bold.TLabel")
        self.lbl_balance = ttk.Label(top, style="Bold.TLabel")
        self.lbl_goal = ttk.Label(top, style="Bold.TLabel")
        self.lbl_remaining = ttk.Label(top, style="Bold.TLabel")

        self.lbl_income.grid(row=0, column=0, padx=20, sticky="w")
        self.lbl_expenses.grid(row=0, column=1, padx=20, sticky="w")
        self.lbl_balance.grid(row=0, column=2, padx=20, sticky="w")
        self.lbl_goal.grid(row=1, column=0, padx=20, sticky="w")
        self.lbl_remaining.grid(row=1, column=1, padx=20, sticky="w")

        pb_frame = ttk.Frame(top, style="Dark.TFrame")
        pb_frame.grid(row=1, column=2, padx=20)
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(pb_frame, variable=self.progress_var,
                                        maximum=100, length=320)
        self.progress.pack()

        body = ttk.Frame(self.tab_dashboard, style="Dark.TFrame")
        body.pack(fill=tk.BOTH, expand=True)

        table_card = ttk.Frame(body, style="Card.TFrame", padding=14)
        table_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        self.tree = ttk.Treeview(
            table_card,
            columns=("id", "date", "type", "category", "description", "amount"),
            displaycolumns=("date", "type", "category", "description", "amount"),
            show="headings"
        )

        for col in ("id", "date", "type", "category", "description", "amount"):
            self.tree.heading(col, text=col.capitalize())

        self.tree.pack(fill=tk.BOTH, expand=True)
        ttk.Button(table_card, text="Delete Selected", style="Accent.TButton",
                   command=self.delete_selected).pack(pady=10)

        chart_card = ttk.Frame(body, style="Card.TFrame", padding=14)
        chart_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        btns = ttk.Frame(chart_card, style="Card.TFrame")
        btns.pack(pady=5)
        ttk.Button(btns, text="Spending by Category", style="Accent.TButton",
                   command=lambda: self.switch_chart("category")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btns, text="Income vs Expenses", style="Accent.TButton",
                   command=lambda: self.switch_chart("income_expense")).pack(side=tk.LEFT, padx=5)

        self.figure = Figure(figsize=(5.5, 3.4), dpi=100)
        self.figure.patch.set_facecolor(self.card)
        self.chart_canvas = FigureCanvasTkAgg(self.figure, master=chart_card)
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def build_add_transaction(self):
        card = ttk.Frame(self.tab_add, style="Card.TFrame", padding=26)
        card.pack(padx=60, pady=60, fill=tk.X)

        labels = ["Date (YYYY-MM-DD)", "Type", "Category", "Description", "Amount"]
        for i, text in enumerate(labels):
            ttk.Label(card, text=text, foreground=self.gold, background=self.card,
                      font=("Inter", 11, "bold")).grid(row=i, column=0, pady=10, sticky="w")

        self.entry_date = ttk.Entry(card)
        self.entry_date.grid(row=0, column=1, pady=10)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.var_type = tk.StringVar(value="Expense")
        self.combo_type = ttk.Combobox(card, textvariable=self.var_type,
                                       values=["Income", "Expense"], state="readonly")
        self.combo_type.grid(row=1, column=1, pady=10)

        self.var_cat = tk.StringVar()
        self.combo_category = ttk.Combobox(card, textvariable=self.var_cat,
                                           values=["Salary", "Scholarship", "Food", "Rent",
                                                   "Utilities", "Transport", "Entertainment",
                                                   "Savings", "Other"], state="readonly")
        self.combo_category.grid(row=2, column=1, pady=10)

        self.entry_desc = ttk.Entry(card)
        self.entry_desc.grid(row=3, column=1, pady=10)

        self.entry_amount = ttk.Entry(card)
        self.entry_amount.grid(row=4, column=1, pady=10)

        ttk.Button(card, text="Add Transaction", style="Accent.TButton",
                   command=self.add_transaction).grid(row=5, column=0, columnspan=2, pady=24)

    def build_settings_tab(self):
        card = ttk.Frame(self.tab_settings, style="Card.TFrame", padding=26)
        card.pack(padx=60, pady=60, fill=tk.X)

        ttk.Label(card, text="Monthly Savings Goal ($)", foreground=self.gold,
                  background=self.card, font=("Inter", 13, "bold")).pack(anchor="w")
        self.var_goal = tk.StringVar(value=str(self.settings["monthly_savings_goal"]))
        ttk.Entry(card, textvariable=self.var_goal).pack(fill=tk.X, pady=14)
        ttk.Button(card, text="Save Goal", style="Accent.TButton",
                   command=self.save_goal).pack(pady=10)

    def add_transaction(self):
        try:
            date_val = datetime.strptime(self.entry_date.get().strip(), "%Y-%m-%d")
        except:
            messagebox.showerror("Invalid Date", "Please use YYYY-MM-DD.")
            return
        try:
            amt = float(self.entry_amount.get().strip())
        except:
            messagebox.showerror("Invalid Amount", "Enter a number.")
            return
        s = SessionLocal()
        tx = Transaction(
            date=date_val,
            type=self.var_type.get(),
            category=self.var_cat.get(),
            description=self.entry_desc.get().strip(),
            amount=amt,
        )
        s.add(tx)
        s.commit()
        s.close()
        self.transactions_df = self.load_transactions_df()
        self.refresh_dashboard()
        messagebox.showinfo("Success", "Transaction added.")

    def save_goal(self):
        try:
            goal = float(self.var_goal.get())
        except:
            messagebox.showerror("Invalid Goal", "Must be a number.")
            return
        self.settings["monthly_savings_goal"] = goal
        self.save_setting("monthly_savings_goal", goal)
        self.refresh_dashboard()
        messagebox.showinfo("Saved", "Goal updated.")

    def refresh_dashboard(self):
        if self.transactions_df.empty:
            month_df = pd.DataFrame(columns=self.transactions_df.columns)
        else:
            now = datetime.now()
            month_df = self.transactions_df[
                (self.transactions_df["date"].dt.year == now.year)
                & (self.transactions_df["date"].dt.month == now.month)
            ]
        income = month_df[month_df["type"] == "Income"]["amount"].sum()
        expenses = month_df[month_df["type"] == "Expense"]["amount"].sum()
        net = income - expenses
        goal = self.settings["monthly_savings_goal"]
        remaining = max(goal - max(net, 0), 0)
        progress = min(max(net, 0) / goal * 100 if goal > 0 else 0, 100)
        self.lbl_income["text"] = f"Income: ${income:,.2f}"
        self.lbl_expenses["text"] = f"Expenses: ${expenses:,.2f}"
        self.lbl_balance["text"] = f"Net: ${net:,.2f}"
        self.lbl_goal["text"] = f"Goal: ${goal:,.2f}"
        self.lbl_remaining["text"] = f"Remaining: ${remaining:,.2f}"
        self.progress_var.set(progress)
        for r in self.tree.get_children():
            self.tree.delete(r)
        for _, r in month_df.sort_values("date").iterrows():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    int(r["id"]),
                    r["date"].strftime("%Y-%m-%d"),
                    r["type"],
                    r["category"],
                    r.get("description", ""),
                    f"${r['amount']:,.2f}",
                ),
            )
        self.draw_chart()

    def switch_chart(self, name):
        self.current_chart = name
        self.draw_chart()

    def draw_chart(self):
        df = self.transactions_df
        now = datetime.now()
        df = df[
            (df["date"].dt.year == now.year)
            & (df["date"].dt.month == now.month)
        ]
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(self.card)
        ax.tick_params(colors=self.text)
        if df.empty:
            ax.text(0.5, 0.5, "No Data", ha="center", color=self.text)
        else:
            if self.current_chart == "category":
                ex = df[df["type"] == "Expense"]
                if ex.empty:
                    ax.text(0.5, 0.5, "No Expenses", ha="center", color=self.text)
                else:
                    group = ex.groupby("category")["amount"].sum()
                    ax.bar(group.index, group.values, color=self.accent)
                    ax.set_title("Spending by Category", color=self.text)
            else:
                inc = df[df["type"] == "Income"]["amount"].sum()
                out = df[df["type"] == "Expense"]["amount"].sum()
                ax.bar(["Income", "Expenses"], [inc, out], color=["#00E8A2", "#FF6F6F"])
                ax.set_title("Income vs Expenses", color=self.text)
        self.figure.tight_layout()
        self.chart_canvas.draw()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showerror("Error", "Select a row.")
            return
        tx_id = self.tree.item(sel[0])["values"][0]
        s = SessionLocal()
        deleted = s.query(Transaction).filter(Transaction.id == tx_id).delete()
        s.commit()
        s.close()
        if deleted:
            self.transactions_df = self.load_transactions_df()
            self.refresh_dashboard()
            messagebox.showinfo("Deleted", "Transaction removed.")
        else:
            messagebox.showerror("Error", "Could not delete.")


def main():
    root = tk.Tk()
    BudgetWiseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
