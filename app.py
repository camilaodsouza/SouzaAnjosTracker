from datetime import datetime
import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = "expenses.json"
RECURRING_FILE = "recurring.json"

st.title("Controle Cartão de  Crédito")

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

def load_recurring():
    if os.path.exists(RECURRING_FILE):
        try:
            with open(RECURRING_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_recurring(data):
    with open(RECURRING_FILE, "w") as f:
        json.dump(data, f, indent=2)

def generate_recurring_expenses():

    today = pd.Timestamp.today()

    for rule in st.session_state.recurring:

        start = pd.Timestamp(rule["start_date"])

        months_diff = (today.year - start.year) * 12 + (today.month - start.month)

        limit = months_diff + 1

        if rule["type"] == "parcelamento" and rule["months"]:
            limit = min(limit, rule["months"])

        for i in range(limit):

            expense_date = (start + pd.DateOffset(months=i)).strftime("%Y-%m-%d")

            exists = any(
                e["description"] == rule["description"] and e["date"] == expense_date
                for e in st.session_state.expenses
            )

            if not exists:
                st.session_state.expenses.append({
                    "description": rule["description"],
                    "amount": rule["amount"],
                    "date": expense_date
                })
 
# session state init
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

if "recurring" not in st.session_state:
    st.session_state.recurring = load_recurring()

# add new expense 
st.write("Nova Despesa")

expense_type = st.selectbox(
    "Tipo",
    ["Única", "Recorrente", "Parcelamento"]
)

with st.form("expense_form", clear_on_submit=True):

    description = st.text_input("Descrição")
    amount = st.number_input("Valor", min_value=0.0, step=1.0)

    start_date = st.date_input("Data de Início")
    months = None

    if expense_type == "Parcelamento":
        months = st.number_input("Número de Parcelas", min_value=1)

    submitted = st.form_submit_button("Salvar")

    if submitted:

        if expense_type == "Única":

            new_expense = {
                "description": description,
                "amount": amount,
                "date": start_date.isoformat()
            }

            st.session_state.expenses.append(new_expense)
        
        elif expense_type == "Recorrente":

            new_recurring = {
                "description": description,
                "amount": amount,
                "start_date": start_date.isoformat(),
                "type": "recorrente"
            }

            st.session_state.recurring.append(new_recurring)

        elif expense_type == "Parcelamento":

            start = pd.Timestamp(start_date)

            for i in range(int(months)):

                expense_date = (start + pd.DateOffset(months=i)).strftime("%Y-%m-%d")

                new_expense = {
                    "description": description,
                    "amount": amount,
                    "date": expense_date
                }

                st.session_state.expenses.append(new_expense)

        save_expenses(st.session_state.expenses)
        save_recurring(st.session_state.recurring)

        st.success("Salvo com sucesso")

def generate_recurring_expenses():

    today = pd.Timestamp.today()

    for rule in st.session_state.recurring:

        start = pd.Timestamp(rule["start_date"])

        months_diff = (today.year - start.year) * 12 + (today.month - start.month)

        limit = months_diff + 12

        for i in range(limit + 1):

            expense_date = (start + pd.DateOffset(months=i)).strftime("%Y-%m-%d")

            exists = any(
                e["description"] == rule["description"] and e["date"] == expense_date
                for e in st.session_state.expenses
            )

            if not exists:

                st.session_state.expenses.append({
                    "description": rule["description"],
                    "amount": rule["amount"],
                    "date": expense_date
                })

generate_recurring_expenses()
save_expenses(st.session_state.expenses)

st.write("## Filtro")

# collect available months
months = sorted({expense["date"][:7] for expense in st.session_state.expenses},  reverse=True)

current_month = datetime.today().strftime("%Y-%m")

default_index = months.index(current_month) if current_month in months else 0

selected_month = st.selectbox(
    "Selecione o mês",
    months,
    index=default_index
)

if selected_month:
    filtered_expenses = [
        e for e in st.session_state.expenses
        if e["date"].startswith(selected_month)
    ]
else:
    filtered_expenses = st.session_state.expenses

st.write("## Gasto Total Mensal")

total = sum(expense["amount"] for expense in filtered_expenses)
st.write(f"R${total:,.2f}")

tab1, tab2 = st.tabs(["Despesas Mensais", "Despesas Recorrentes Ativas"])

with tab1: 
    st.write("## Despesas")

    if filtered_expenses:

        for i, expense in enumerate(filtered_expenses):

            col1, col2, col3, col4 = st.columns([3,2,2,1])

            with col1:
                st.write(expense["description"])

            with col2:
                st.write(expense["date"])

            with col3:
                st.write(f"R$ {expense['amount']:,.2f}")

            with col4:
                if st.button("🗑️", key=f"del_{i}"):

                    st.session_state.expenses.remove(expense)
                    save_expenses(st.session_state.expenses)
                    st.rerun()

    else:
        st.write("Sem despesas.")

with tab2:

    st.write("## Recorrentes Ativas")

    if st.session_state.recurring:

        for i, rule in enumerate(st.session_state.recurring):

            col1, col2, col3, col4 = st.columns([3,2,2,1])

            with col1:
                st.write(rule["description"])

            with col2:
                st.write(f"R$ {rule['amount']:,.2f}")

            with col3:
                st.write(f"Início: {rule['start_date']}")

            with col4:
                if st.button("🗑️", key=f"rec_{i}"):

                    # remove regra
                    st.session_state.recurring.remove(rule)

                    # remove despesas geradas por ela
                    st.session_state.expenses = [
                        e for e in st.session_state.expenses
                        if e["description"] != rule["description"]
                    ]

                    save_recurring(st.session_state.recurring)
                    save_expenses(st.session_state.expenses)

                    st.rerun()

    else:
        st.write("Nenhuma despesa recorrente.")

