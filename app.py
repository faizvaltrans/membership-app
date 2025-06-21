# app.py
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import os

MEMBERS_FILE = "members.csv"
PAYMENTS_FILE = "payments.csv"

st.set_page_config(page_title="Membership Manager", layout="wide")

# Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Admin Login")
    password = st.text_input("Enter admin password", type="password")
    if st.button("Login"):
        if password == "admin123":
            st.session_state.logged_in = True
        else:
            st.error("Incorrect password")

def load_data():
    members = pd.read_csv(MEMBERS_FILE) if os.path.exists(MEMBERS_FILE) else pd.DataFrame(columns=[
        "Member ID", "Full Name", "Initial", "Father's Name", "Emirate", "Phone", "Address", "Remarks", "Photo URL"
    ])
    payments = pd.read_csv(PAYMENTS_FILE) if os.path.exists(PAYMENTS_FILE) else pd.DataFrame(columns=[
        "Payment ID", "Member ID", "Name", "Amount", "Date", "Notes"
    ])
    return members, payments

def save_data(members, payments):
    members.to_csv(MEMBERS_FILE, index=False)
    payments.to_csv(PAYMENTS_FILE, index=False)

def member_section(members):
    st.subheader("👥 Manage Members")
    tab1, tab2 = st.tabs(["Add/Edit Member", "Member List"])
    with tab1:
        with st.form("member_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name")
                initial = st.text_input("Initial")
                father = st.text_input("Father's Name")
                emirate = st.text_input("Emirate")
                phone = st.text_input("Phone")
            with col2:
                address = st.text_area("Address")
                remarks = st.text_input("Remarks")
                photo_url = st.text_input("Photo URL (optional)")
            if st.form_submit_button("Save Member"):
                member_id = str(uuid.uuid4())[:8]
                members = pd.concat([members, pd.DataFrame([{
                    "Member ID": member_id,
                    "Full Name": full_name,
                    "Initial": initial,
                    "Father's Name": father,
                    "Emirate": emirate,
                    "Phone": phone,
                    "Address": address,
                    "Remarks": remarks,
                    "Photo URL": photo_url
                }])], ignore_index=True)
                st.success(f"Member '{full_name}' added.")
    with tab2:
        search = st.text_input("🔍 Search Members")
        filtered = members[members.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)] if search else members
        st.dataframe(filtered, use_container_width=True)

def payment_section(members, payments):
    st.subheader("💸 Payments") 
    tab1, tab2 = st.tabs(["Add Payment", "Payment History"])
    with tab1:
        if not members.empty:
            member_list = members[["Member ID", "Full Name"]].astype(str)
            selection = st.selectbox("Select Member", member_list.apply(lambda x: f"{x['Member ID']} - {x['Full Name']}", axis=1))
            if selection:
                member_id, name = selection.split(" - ", 1)
                amount = st.number_input("Amount (AED)", min_value=0.0, step=10.0)
                date = st.date_input("Date", value=datetime.now())
                notes = st.text_input("Notes (optional)")
                if st.button("Save Payment"):
                    payment_id = str(uuid.uuid4())[:8]
                    payments = pd.concat([payments, pd.DataFrame([{
                        "Payment ID": payment_id,
                        "Member ID": member_id,
                        "Name": name,
                        "Amount": amount,
                        "Date": date,
                        "Notes": notes
                    }])], ignore_index=True)
                    st.success(f"Payment saved for {name}.")
        else:
            st.warning("No members found. Please add a member first.")
    with tab2:
        search = st.text_input("🔍 Search Payments")
        filtered = payments[payments.apply(lambda row: search.lower() in row.astype(str).str.lower().to_string(), axis=1)] if search else payments
        st.dataframe(filtered, use_container_width=True)

def main():
    if not st.session_state.logged_in:
        login()
        return
    st.title("🧾 Membership Manager")
    members, payments = load_data()
    member_section(members)
    payment_section(members, payments)
    save_data(members, payments)

if __name__ == '__main__':
    main()
