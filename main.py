import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(layout="wide")

name = "Cris"
OPTIONS = [
    "Food", "Transportation", "Clothes",
    "Personal Care", "Travel",
    "Lifestyle", "Bills", "Others"
]

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "type_input" not in st.session_state:
    st.session_state.type_input = None

if "amount_input" not in st.session_state:
    st.session_state.amount_input = ""

if "expenses_dict" not in st.session_state:
    st.session_state.expenses_dict = {}

if "transaction_list" not in st.session_state:
    st.session_state.transaction_list = []

if "total_expenses" not in st.session_state:
    st.session_state.total_expenses = 0


def handle_submit():
    expense_type = st.session_state.type_input
    amount = st.session_state.amount_input

    if not expense_type:
        st.toast("Please select a type first")
        return

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        st.toast("Please enter a valid amount")
        return

    st.session_state.expenses_dict[expense_type] = (
        st.session_state.expenses_dict.get(expense_type, 0) + amount
    )

    st.session_state.transaction_list.append(
        {"Type": expense_type, "Amount": amount}
    )

    st.toast("Expense Added Successfully!")

    st.session_state.type_input = None
    st.session_state.amount_input = ""

@st.dialog("Confimation")
def clear_expenses():
    st.write("Are you sure, you want to clear your expenses?")

    col1, col2 = st.columns(2)
    if col1.button("Yes"):
        st.session_state.expenses_dict = {}
        st.session_state.transaction_list = []
        st.session_state.total_expenses = 0
        st.rerun()
    if col2.button("No"):
        st.rerun()

def get_expense_df():
    types = [keys for keys, values in st.session_state.expenses_dict.items()]
    amounts = [values for keys, values in st.session_state.expenses_dict.items()]

    data = {
        "Type": types,
        "Amount": amounts
    }

    df = pd.DataFrame(data)
    return df

def recalculate_expenses():
    new_dict = {}

    for item in st.session_state.transaction_list:
        expense_type = item["Type"]
        amount = float(item["Amount"])

        new_dict[expense_type] = new_dict.get(expense_type, 0) + amount

    st.session_state.expenses_dict = new_dict

def get_total_expenses():
    total = 0
    for n in range (0, len(st.session_state.transaction_list)):
        total += st.session_state.transaction_list[n]["Amount"]
    return total


nav1, nav2, nav3, nav4, nav5 = st.columns(5, gap="small")

if nav1.button("Dashboard", use_container_width=True):
    st.session_state.page = "Dashboard"

if nav2.button("Transaction", use_container_width=True):
    st.session_state.page = "Transaction"

if nav5.button("About", use_container_width=True):
    st.session_state.page = "About"

st.divider()

if st.session_state.page == "Dashboard":

    st.title(f"Welcome, {name}")

    col1, col2 = st.columns(2)

    col1.subheader("My Expenses")

    if not st.session_state.expenses_dict:
        col1.info("No expenses yet")
    else:
        df = get_expense_df()
        fig = px.pie(df, names="Type", values="Amount")
        col1.plotly_chart(fig, use_container_width=True)

    col2.subheader("Recent Expenses")

    if not st.session_state.transaction_list:
        col2.info("No recent expenses")
    else:
        col2.dataframe(
            pd.DataFrame(st.session_state.transaction_list),
            use_container_width=True, hide_index=True, row_height=50
        )
    
    st.session_state.total_expenses = get_total_expenses()
    col2.subheader(f"Total: {st.session_state.total_expenses:,.2f}")


elif st.session_state.page == "Transaction":

    st.title("Transaction Page")

    col1, col2 = st.columns(2)

    col1.subheader("Add Expense")

    col1.selectbox(
        "Select Expense Type",
        OPTIONS,
        key="type_input",
        placeholder="Choose type"
    )

    col1.text_input("Amount", key="amount_input")

    col1.button(
        "Add",
        on_click=handle_submit,
        use_container_width=True
    )

    col2.subheader("Modify Expenses")

    if not st.session_state.transaction_list:
        col2.info("No transactions yet")
    else:
        edited_df = col2.data_editor(
            pd.DataFrame(st.session_state.transaction_list),
            num_rows="dynamic",
            use_container_width=True,
            height=300
        )

        st.session_state.transaction_list = edited_df.to_dict("records")
        recalculate_expenses()

    if col2.button(
        "Clear All",
        use_container_width=True
    ):
        if not st.session_state.transaction_list:
            st.toast("No expenses yet")
        else:
            clear_expenses()

elif st.session_state.page == "About":

    st.title("About Page")
    st.write("Simple expense tracker built with Streamlit.")