from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ----------------------------------
# Database Connection
# ----------------------------------
def get_db_connection():
    conn = sqlite3.connect("employees.db")
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------------------
# Dashboard + Search
# ----------------------------------
@app.route("/")
def dashboard():

    search = request.args.get("search", "")

    conn = get_db_connection()

    if search:

        employees = conn.execute("""
            SELECT * FROM employees
            WHERE
                name LIKE ?
                OR department LIKE ?
                OR position LIKE ?
            ORDER BY id
        """, (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:

        employees = conn.execute(
            "SELECT * FROM employees ORDER BY id"
        ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        employees=employees,
        search=search
    )


# ----------------------------------
# Add Employee
# ----------------------------------
@app.route("/add", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        name = request.form["name"]
        department = request.form["department"]
        position = request.form["position"]
        salary = request.form["salary"]
        status = request.form["status"]

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO employees
            (name, department, position, salary, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            department,
            position,
            salary,
            status
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_employee.html")


# ----------------------------------
# Edit Employee
# ----------------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_employee(id):

    conn = get_db_connection()

    employee = conn.execute(
        "SELECT * FROM employees WHERE id=?",
        (id,)
    ).fetchone()

    if employee is None:
        conn.close()
        return "Employee Not Found"

    if request.method == "POST":

        name = request.form["name"]
        department = request.form["department"]
        position = request.form["position"]
        salary = request.form["salary"]
        status = request.form["status"]

        conn.execute("""
            UPDATE employees
            SET
                name=?,
                department=?,
                position=?,
                salary=?,
                status=?
            WHERE id=?
        """, (
            name,
            department,
            position,
            salary,
            status,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    conn.close()

    return render_template(
        "edit_employee.html",
        employee=employee
    )


# ----------------------------------
# Delete Employee
# ----------------------------------
@app.route("/delete/<int:id>")
def delete_employee(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM employees WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# ----------------------------------
# Run Flask
# ----------------------------------
if __name__ == "__main__":
    app.run(debug=True)