from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os
import re

# ----------------------------------
# Load Environment Variables
# ----------------------------------

load_dotenv()

# ----------------------------------
# Flask Application
# ----------------------------------

app = Flask(__name__)


# ----------------------------------
# MongoDB Atlas Connection
# ----------------------------------

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError(
        "MONGO_URI is not set. "
        "Please check your .env file."
    )

client = MongoClient(MONGO_URI)

# MongoDB database
db = client["employee_management_system"]

# Employees collection
employees_collection = db["employees"]


# ----------------------------------
# Test MongoDB Connection
# ----------------------------------

try:

    client.admin.command("ping")

    print("===================================")
    print("MongoDB Atlas connected successfully!")
    print("Database: employee_management_system")
    print("Collection: employees")
    print("===================================")

except PyMongoError as e:

    print("===================================")
    print("MongoDB connection failed!")
    print(e)
    print("===================================")


# ----------------------------------
# Generate Employee ID
# ----------------------------------

def get_next_employee_id():

    last_employee = employees_collection.find_one(
        {},
        sort=[("id", -1)]
    )

    if last_employee and "id" in last_employee:

        return int(last_employee["id"]) + 1

    return 1


# ----------------------------------
# Dashboard
# ----------------------------------

@app.route("/")
def dashboard():

    search = request.args.get("search", "").strip()

    # ----------------------------------
    # Search Employees
    # ----------------------------------

    if search:

        search_regex = re.compile(
            re.escape(search),
            re.IGNORECASE
        )

        employees = list(
            employees_collection.find(
                {
                    "$or": [
                        {"name": search_regex},
                        {"department": search_regex},
                        {"position": search_regex}
                    ]
                }
            ).sort("id", 1)
        )

    else:

        employees = list(
            employees_collection.find().sort("id", 1)
        )


    # ----------------------------------
    # Dashboard Statistics
    # ----------------------------------

    total_employees = employees_collection.count_documents({})


    # Find unique departments

    departments = employees_collection.distinct(
        "department"
    )

    departments = [
        department
        for department in departments
        if department
    ]

    total_departments = len(departments)


    # Projects not implemented yet

    total_projects = 0


    # Attendance not implemented yet

    attendance = 100


    # ----------------------------------
    # Render Dashboard
    # ----------------------------------

    return render_template(
        "dashboard.html",
        employees=employees,
        search=search,
        total_employees=total_employees,
        total_departments=total_departments,
        total_projects=total_projects,
        attendance=attendance
    )


# ----------------------------------
# Employees Page
# ----------------------------------

@app.route("/employees")
def employees():

    employees = list(
        employees_collection.find().sort("id", 1)
    )

    return render_template(
        "employees.html",
        employees=employees
    )


# ----------------------------------
# Departments Page
# ----------------------------------

@app.route("/departments")
def departments():

    department_data = employees_collection.aggregate(
        [
            {
                "$group": {
                    "_id": "$department",
                    "total": {
                        "$sum": 1
                    }
                }
            },
            {
                "$sort": {
                    "_id": 1
                }
            }
        ]
    )

    departments = []

    for department in department_data:

        departments.append(
            {
                "department": department["_id"],
                "total": department["total"]
            }
        )

    return render_template(
        "departments.html",
        departments=departments
    )


# ----------------------------------
# Reports Page
# ----------------------------------

@app.route("/reports")
def reports():

    total_employees = employees_collection.count_documents({})


    departments = employees_collection.distinct(
        "department"
    )

    departments = [
        department
        for department in departments
        if department
    ]

    total_departments = len(departments)


    return render_template(
        "reports.html",
        total_employees=total_employees,
        total_departments=total_departments
    )


# ----------------------------------
# Settings Page
# ----------------------------------

@app.route("/settings")
def settings():

    return render_template(
        "settings.html"
    )


# ----------------------------------
# Logout
# ----------------------------------

@app.route("/logout")
def logout():

    return redirect("/")


# ----------------------------------
# Add Employee
# ----------------------------------

@app.route("/add", methods=["GET", "POST"])
def add_employee():

    if request.method == "POST":

        name = request.form["name"].strip()

        department = request.form["department"].strip()

        position = request.form["position"].strip()

        salary = request.form["salary"].strip()

        status = request.form["status"].strip()


        # Generate ID

        employee_id = get_next_employee_id()


        # Employee document

        employee = {

            "id": employee_id,

            "name": name,

            "department": department,

            "position": position,

            "salary": salary,

            "status": status

        }


        # Insert into MongoDB

        employees_collection.insert_one(
            employee
        )


        return redirect("/")


    return render_template(
        "add_employee.html"
    )


# ----------------------------------
# Edit Employee
# ----------------------------------

@app.route(
    "/edit/<int:id>",
    methods=["GET", "POST"]
)
def edit_employee(id):

    employee = employees_collection.find_one(
        {
            "id": id
        }
    )


    if employee is None:

        return "Employee Not Found", 404


    # ----------------------------------
    # Update Employee
    # ----------------------------------

    if request.method == "POST":

        name = request.form["name"].strip()

        department = request.form["department"].strip()

        position = request.form["position"].strip()

        salary = request.form["salary"].strip()

        status = request.form["status"].strip()


        employees_collection.update_one(

            {
                "id": id
            },

            {
                "$set": {

                    "name": name,

                    "department": department,

                    "position": position,

                    "salary": salary,

                    "status": status

                }
            }

        )


        return redirect("/")


    return render_template(

        "edit_employee.html",

        employee=employee

    )


# ----------------------------------
# Delete Employee
# ----------------------------------

@app.route("/delete/<int:id>")
def delete_employee(id):

    employees_collection.delete_one(

        {
            "id": id
        }

    )

    return redirect("/")


# ----------------------------------
# Run Flask Application
# ----------------------------------

if __name__ == "__main__":

    app.run(
        debug=True
    )