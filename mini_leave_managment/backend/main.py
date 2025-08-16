from flask import Flask, request, jsonify
from datetime import datetime
from dotenv import load_dotenv
import connections

load_dotenv()
app = Flask(__name__)


@app.route('/employee', methods=['POST'])
def add_employee():
    try:
        data = request.get_json()
        name = data.get("name")
        joining_date = data.get("joining_date")
        leave_balance = data.get("leave_balance", 30)

        # Validation
        try:
            datetime.strptime(joining_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"})

        if not name:
            return jsonify({"error": "Name is required"})

        conn = connections.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name, joining_date, total_leave_balance) VALUES (%s, %s, %s)",
            (name, joining_date, leave_balance)
        )
        conn.commit()
        emp_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({"message": "Employee added successfully", "employee_id": emp_id})

    except Exception as e:
        return jsonify({"error": str(e)})

# Apply for leave
@app.route("/apply-leave", methods=["POST"])
def apply_leave():
    data = request.json
    employee_id = data.get("employee_id")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    conn = connections.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE id=%s", (employee_id,))
    employee = cursor.fetchone()
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    if datetime.strptime(start_date, "%Y-%m-%d").date() < employee["joining_date"]:
        return jsonify({"error": "Leave cannot be before joining date"}), 400


    if datetime.strptime(end_date, "%Y-%m-%d") < datetime.strptime(start_date, "%Y-%m-%d"):
        return jsonify({"error": "End date cannot be before start date"}), 400


    days_requested = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1


    if days_requested > employee["total_leave_balance"]:
        return jsonify({"error": "Not enough leave balance"}), 400


    cursor.execute("""
        SELECT * FROM leave_requests
        WHERE employee_id=%s AND status='approved'
        AND (start_date <= %s AND end_date >= %s)
    """, (employee_id, end_date, start_date))
    if cursor.fetchone():
        return jsonify({"error": "Leave dates overlap with existing approved leave"}), 400


    cursor.execute("""
        INSERT INTO leave_requests (employee_id, start_date, end_date, days_requested)
        VALUES (%s, %s, %s, %s)
    """, (employee_id, start_date, end_date, days_requested))
    cursor.execute("SELECT id FROM leave_requests ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    leave_id = row['id'] if row else None
    conn.commit()

    return jsonify({"message": "Leave request submitted", "days_requested": days_requested,"leave_id":leave_id}), 201

# Approve or Reject leave
@app.route("/approve-leave/<int:leave_id>", methods=["PUT"])
def approve_leave(leave_id):
    data = request.json
    print(data)
    status = data.get('status').upper()
    print("status",status)
    if status not in ['APPROVED', 'REJECTED']:
        return jsonify({"error": "Invalid status. Must be 'APPROVED' or 'REJECTED'."}), 400

    conn = connections.get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get leave details
    cursor.execute("SELECT * FROM leave_requests WHERE id = %s", (leave_id,))
    leave = cursor.fetchone()
    if not leave:
        cursor.close()
        conn.close()
        return jsonify({"error": "Leave not found"}), 404

    if status == 'APPROVED':
        days_requested = (leave['end_date'] - leave['start_date']).days + 1

        cursor.execute("SELECT total_leave_balance FROM employees WHERE id = %s", (leave['employee_id'],))
        emp = cursor.fetchone()

        if emp['total_leave_balance'] >= days_requested:
            cursor.execute("""
                UPDATE employees SET total_leave_balance = total_leave_balance - %s WHERE id = %s
            """, (days_requested, leave['employee_id']))

            cursor.execute("""
                INSERT INTO leave_transactions (employee_id, leave_id, transaction_type, days, remarks)
                VALUES (%s, %s, 'DEBIT', %s, 'Leave Approved')
            """, (leave['employee_id'], leave_id, days_requested))
        else:
            cursor.close()
            conn.close()
            return jsonify({"error": "Not enough leave balance"}), 400

    elif status == 'REJECTED':
        cursor.execute("""
            INSERT INTO leave_transactions (employee_id, leave_id, transaction_type, days, remarks)
            VALUES (%s, %s, 'NONE', 0, 'Leave Rejected')
        """, (leave['employee_id'], leave_id))

    cursor.execute("""
        UPDATE leave_requests SET status = %s WHERE id = %s
    """, (status, leave_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": f"Leave {status.lower()} successfully",
        "leave_id": leave_id,
        "status": status
    })


# Check leave balance
@app.route("/leave-balance/<int:employee_id>", methods=["GET"])
def leave_balance(employee_id):
    cached_balance = connections.redis_client.get(f"leave_balance:{employee_id}")
    if cached_balance is not None:
        return jsonify({"leave_balance": int(cached_balance)})
    conn = connections.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT total_leave_balance FROM employees WHERE id=%s", (employee_id,))
    emp = cursor.fetchone()
    connections.redis_client.setex(f"leave_balance:{employee_id}", 3600, emp["total_leave_balance"])
    if not emp:
        return jsonify({"error": "Employee not found"}), 404
    return jsonify({"leave_balance": emp["total_leave_balance"]})

if __name__ == "__main__":
    app.run(debug=True)