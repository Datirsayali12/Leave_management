import streamlit as st
import requests
from datetime import date

BASE_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Leave Management System", layout="centered")

st.title("Leave Management System")

menu = st.sidebar.radio("Menu", ["Add Employee", "Apply for Leave", "Approve/Reject Leave", "Leave Balance"])
if menu == "Add Employee":
    st.header("Add New Employee")
    name = st.text_input("Name")
    email = st.text_input("Email")
    dept = st.text_input("Department")
    joining_date = st.date_input("Joining Date", date.today())
    leave_balance = st.number_input("Leave Balance", 0, 100, 20)

    if st.button("Submit"):
        try:
            res = requests.post(f"{BASE_URL}/employee", json={
                "name": name,
                "email": email,
                "department": dept,
                "joining_date": str(joining_date),
                "leave_balance": leave_balance
            })

            # Debug: Show status code & raw response
            st.write("Status:", res.status_code)
            st.write("message:", res.text)

            if res.headers.get("Content-Type", "").startswith("application/json"):
                data = res.json()
                if res.status_code == 200 or res.status_code == 201:
                    st.success(data.get("message", "Success"))
                else:
                    st.error(data.get("error", "Unknown error"))
            else:
                st.error("Unexpected response format (not JSON).")

        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")


elif menu == "Apply for Leave":
    st.header("Apply for Leave")
    emp_id = st.number_input("Employee ID", 1)
    start_date = st.date_input("Start Date", date.today())
    end_date = st.date_input("End Date", date.today())
    reason = st.text_area("Reason")

    if st.button("Apply"):
        res = requests.post(f"{BASE_URL}/apply-leave", json={
            "employee_id": emp_id,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "reason": reason
        })
        print(res.text)
        st.write(res.json())

elif menu == "Approve/Reject Leave":
    st.header("Approve/Reject Leave")

    leave_id = st.number_input("Leave ID", min_value=1, step=1)

    # Keep the status selection persistent across reruns
    status = st.selectbox(
        "Status",
        ["approved", "rejected"],
        key="leave_status"  # Persist selection
    )

    if st.button("Update Status"):
        payload = {"status": status}
        res = requests.put(f"{BASE_URL}/approve-leave/{leave_id}", json=payload)

        try:
            st.write("Response:", res.json())
        except Exception:
            st.error("Invalid response from server")

elif menu == "Leave Balance":
    st.header("Check Leave Balance")
    emp_id = st.number_input("Employee ID", 1)

    if st.button("Get Balance"):
        res = requests.get(f"{BASE_URL}/leave-balance/{emp_id}")
        st.write(res.json())
