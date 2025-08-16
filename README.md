
# Mini Leave Management System (LMS)

A simple Leave Management System for a startup with 50 employees.  
HR can **add employees**, **apply/approve/reject leaves**, and **track leave balance**.

## Features
- **Add Employee** – Name, Email, Department, Joining Date
- **Apply Leave** – Employees can request leave (start & end dates)
- **Approve/Reject Leave** – HR can manage leave requests
- **Track Leave Balance** – View remaining leave days for each employee
- **Edge Case Handling** – Invalid dates, overlapping leaves, insufficient balance, etc.

## Tech Stack

- **Backend:** Python (Flask)
- **Database:** MySQL
- **Frontend:** streamlit
- **API Style:** REST

## Getting Started

To get started with this repository, follow these steps:

## Installation

1. Create virtual enviroment and activate 
     ```bash
    python -m venv venv
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
  
## API Reference

```http
    POST /employee

```

| Parameter      | Type     | Description                                  |
| :------------- | :------- | :------------------------------------------- |
| `name`         | `string` | **Required**. Full name of the employee      |
| `joining_date` | `string` | **Required**. Date when the employee joined (YYYY-MM-DD) |
| `leave_balance`| `number` | **Required**. Total available leave days     |



```http
  POST /apply-leave

```

| Parameter     | Type     | Description                                             |
| :------------ | :------- | :------------------------------------------------------ |
| `employee_id` | `number` | **Required**. Unique ID of the employee applying for leave |
| `start_date`  | `string` | **Required**. Leave start date in YYYY-MM-DD format     |
| `end_date`    | `string` | **Required**. Leave end date in YYYY-MM-DD format       |

```http
  PUT /approve-leave/<int:leave_id>


```


```http
  GET /leave-balance/<int:employee_id>

```

**Frontend Using streamlit**

## Add Employee API
![Add Employee API Screenshot](https://github.com/Datirsayali12/Leave_management/blob/main/mini_leave_managment/screenshot/add_emp.png)

## Apply Leave API
![Apply Leave API Screenshot](https://github.com/Datirsayali12/Leave_management/blob/main/mini_leave_managment/screenshot/apply_for_leave.png)

## Approve/Reject Leave API 
![Approve/Reject Leave API Screenshot](https://github.com/Datirsayali12/Leave_management/blob/main/mini_leave_managment/screenshot/approve_or_reject_leave.png)

## Leave Balance
![Leave Balance API Screenshot](https://github.com/Datirsayali12/Leave_management/blob/main/mini_leave_managment/screenshot/leave_balance.png)


## Potential Improvements

- **Role-based access** — Separate permissions for HR, Admin, and Employees.
- **Email/SMS notifications** — Notify employees and managers when leave requests are submitted, approved, or rejected.
- **Public holiday/weekend handling** — Automatically exclude public holidays and weekends from leave counts.
- **Leave cancellation option** — Allow employees to cancel approved or pending leaves.
- **Mobile app integration** — Build a mobile-friendly version for better accessibility.
- **Calendar view for leaves** — Visual representation of leaves in a calendar format for quick tracking.
