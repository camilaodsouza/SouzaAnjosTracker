from datetime import date
import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = "expenses.json"

st.title("Credit Card Tracker")

# function to load expenses
def load_expenses():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# function to save expenses
def save_expenses(expenses):
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)

# session state init
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

if "description_input" not in st.session_state:
    st.session_state.description_input = ""

if "amount_input" not in st.session_state:
    st.session_state.amount_input = 0.0

st.write("Add Expense")

with st.form("expense_form", clear_on_submit=True):

    description = st.text_input("Description", key="description_input")
    amount = st.number_input("Amount", min_value=0.0, step=1.0, key="amount_input")

    submitted = st.form_submit_button("Save")

    if submitted:

        new_expense = {
            "description": description,
            "amount": amount,
            "date": date.today().isoformat()
        }

        st.session_state.expenses.append(new_expense)
        save_expenses(st.session_state.expenses)

        st.success("Expense saved")

st.write("## Filter")

# collect available months
months = sorted({expense["date"][:7] for expense in st.session_state.expenses})

if months:
    selected_month = st.selectbox("Select month", months)
else:
    selected_month = None

if selected_month:
    filtered_expenses = [
        e for e in st.session_state.expenses
        if e["date"].startswith(selected_month)
    ]
else:
    filtered_expenses = st.session_state.expenses

st.write("## Monthly Total Spent")

total = sum(expense["amount"] for expense in filtered_expenses)
st.write(f"${total}")

st.write("## Expenses")

if filtered_expenses:

    df = pd.DataFrame(filtered_expenses)

    styled_df = df.style.set_properties(subset=["amount"], **{
    "text-align": "right"
    })

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

else:
    st.write("No expenses for this month.")