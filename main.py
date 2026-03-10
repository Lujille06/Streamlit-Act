import streamlit as st
import plotly.express as px
import pandas as pd
import time

st.set_page_config(layout="wide")

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

if "account_info" not in st.session_state:
    st.session_state.account_info = {
        "name": "Crisartuz Bustenera", 
        "age": 19, "course": "BSIT", 
        "expenses": st.session_state.total_expenses
    }

if "date_input" not in st.session_state:
    st.session_state.date_input = "today"

if "upload_image" not in st.session_state:
    st.session_state.upload_image = None

if "saved_image" not in st.session_state:
    st.session_state.saved_image = "dacshund3.jpg"

if "editing" not in st.session_state:
    st.session_state.editing = False

def handle_submit():
    expense_type = st.session_state.type_input
    amount = st.session_state.amount_input
    date = st.session_state.date_input

    if not expense_type:
        st.toast(":red[Please select a type first]")
        return

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        st.toast(":red[Please enter a valid amount]")
        return

    st.session_state.expenses_dict[expense_type] = (
        st.session_state.expenses_dict.get(expense_type, 0) + amount
    )

    st.session_state.transaction_list.append(
        {"Type": expense_type, "Amount": amount, "Date": date}
    )

    st.toast(":green[Expense Added Successfully!]")

    st.session_state.type_input = None
    st.session_state.amount_input = ""

@st.dialog("Confimation")
def clear_expenses():
    st.write("Are you sure, you want to clear your expenses?")

    col1, col2, col3,  col4, col5 = st.columns(5, gap="xxsmall")
    
    if col1.button(":green[Yes]"):
        st.session_state.expenses_dict = {}
        st.session_state.transaction_list = []
        st.session_state.total_expenses = 0
        st.rerun()

    if col2.button(":red[No]"):
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

def save_image():
    if st.session_state.upload_image is not None:
        st.session_state.saved_image = st.session_state.upload_image

def edit_account():
    st.session_state.editing = not st.session_state.editing

nav1, nav2, nav4, nav5 = st.columns(4, gap="small")

# -- NAVIGATION PANEL --
if nav1.button("Dashboard", use_container_width=True):
    st.session_state.page = "Dashboard"

if nav2.button("Transaction", use_container_width=True):
    st.session_state.page = "Transaction"

if nav4.button("Account", use_container_width=True):
    st.session_state.page = "Account"

if nav5.button("About", use_container_width=True):
    st.session_state.page = "About"

st.divider()

# -- DASHBOARD PAGE --
if st.session_state.page == "Dashboard":

    st.title(f":yellow[Welcome,] :orange[{st.session_state.account_info['name']}]")

    col1, col2 = st.columns(2)

    col1.subheader("My Expenses")

    if not st.session_state.expenses_dict:
        col1.info("To add an expense, navigate to the Transaction page.")
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
    col2.subheader(f"Total Expenses: ₱{st.session_state.total_expenses:,.2f}")

# -- TRANSACTION PAGE --
elif st.session_state.page == "Transaction":

    st.title(":yellow[Transaction Page]")

    col1, col2 = st.columns(2)

    col1.subheader("Add Expense")

    col1.selectbox(
        "Select Expense Type",
        OPTIONS,
        key="type_input",
        placeholder="Choose type"
    )

    col1.text_input("Amount", key="amount_input")

    st.session_state.date_input = col1.date_input("Date", "today")

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
        use_container_width=True,
    ):
        if not st.session_state.transaction_list:
            st.toast("No expenses yet")
        else:
            clear_expenses()

# -- ACCOUNT PAGE --
elif st.session_state.page == "Account":

    st.title(":yellow[Account Page]")

    st.subheader("Profile")

    col1, col2 = st.columns(2, vertical_alignment="center")

    sub1, sub2, sub3 = col1.columns([1,2,1])

    if st.session_state.saved_image is not None:
        sub2.image(st.session_state.saved_image, width=350)

    if not st.session_state.editing:
        col2.subheader("Account Information")
        col2.write(f"Name: {st.session_state.account_info['name']}")
        col2.write(f"Age: {st.session_state.account_info['age']}")
        col2.write(f"Course: {st.session_state.account_info['course']}")
        col2.write(f"Expenses: ₱{st.session_state.total_expenses:,.2f}")
        col2.button("Edit Account", on_click=edit_account, use_container_width=True)

    else: 
        col1.file_uploader("Attach an Image", type=["jpeg", "png", "jpg"], key="upload_image", on_change=save_image)

        col2.subheader("Edit Account")
        new_name = col2.text_input("Name", value=st.session_state.account_info['name'].strip())
        new_age = col2.text_input("Age", value=(st.session_state.account_info['age']))
        new_course = col2.text_input("Course", value=st.session_state.account_info['course'].strip())

        if col2.button("Save changes", use_container_width=True):
            if new_age.isdigit() and int(new_age) > 0 :
                if (
                    str(new_name) != str(st.session_state.account_info['name']) or
                    str(new_age) != str(st.session_state.account_info['age'] )or
                    str(new_course) != str(st.session_state.account_info['course']) 
                ):
                    st.session_state.account_info['name'] = new_name
                    st.session_state.account_info['age'] = new_age
                    st.session_state.account_info['course'] = new_course

                    st.toast(":blue[In progress...]")
                    time.sleep(3)

            st.session_state.editing = False
            st.rerun()         

# -- ABOUT PAGE --
else:
    st.title(":yellow[About Page]")

    col1, col2, col3 = st.columns(3, gap="small", border=True)

    col1.subheader(":yellow[What the app does]")
    col1.markdown("This application serves as a personal financial assistant for students. " \
    "It tracks every expenses and visualizes spending patterns through a dashboard pie chart, " \
    "helping users assess their habits and reduce unnecessary costs effectively.", text_alignment="justify")
    
    col2.subheader(":yellow[Who the target user is]")
    col2.markdown("Although this app can be used by almost everyone, my target user is budget-conscious " \
    "students who often manage their own allowance.", text_alignment="justify")

    col3.subheader(":yellow[What input does the app collect and what output does it shows]")
    col3.markdown("The application prompts users to input the expense type, amount, and date on the transaction page; " \
    "this data is then visualized as a pie chart on the dashboard to illustrate spending percentages.", text_alignment="justify")