# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

# Initialize Flask app
app = Flask(__name__)
app.template_folder = '../templates/'  # Configuring the template folder


# Function to create the SQLite database and tables
def create_tables():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT, contact TEXT)''')  # Add 'contact' column
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY,
                 employee_id INTEGER, 
                 employee_name TEXT,
                 month INTEGER, 
                 day INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS salary
                 (id INTEGER PRIMARY KEY,
                 date TEXT,
                 employee_id INTEGER, 
                 advance INTEGER)''')  # Add 'salary' table
    conn.commit()
    conn.close()


# Call function to create tables
create_tables()


# Route to display the Admin tab
@app.route('/')
def index():

    # Dummy data for months and days (you can replace this with actual data)
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    days = list(range(1, 32))  # Assuming all months have 31 days

    # Define the number of days in each month
    days_in_month = {
        "January": 31,
        "February": 28,  # Assuming non-leap year
        "March": 31,
        "April": 30,
        "May": 31,
        "June": 30,
        "July": 31,
        "August": 31,
        "September": 30,
        "October":+ 31,
        "November": 30,
        "December": 31
    }
    # Fetch employees from the database
    conn = sqlite3.connect('attendance.db')
    # Enable row factory
    conn.row_factory = sqlite3.Row

    # Create a cursor
    c = conn.cursor()

    # Execute the query
    c.execute("SELECT * FROM employees")

    # Fetch all rows as dictionaries
    rows = c.fetchall()

    # Convert rows into a list of dictionaries
    employees = [dict(row) for row in rows]

    # Now each item in the 'employees' list is a dictionary with column names as keys
    print(employees)

    # Fetch attendance records for each employee and each day
    attendance_records = {}
    for employee in employees:
        employee_id = employee['id']
        attendance_records[employee_id] = {}
        for month in months:
            attendance_records[employee_id][month] = {}
            for day in range(1, days_in_month[month] + 1):
                attendance_records[employee_id][month][day] = False  # Initialize as unchecked

    # Execute the query to fetch attendance records
    c.execute("SELECT employee_id, month, day FROM attendance")
    rows = c.fetchall()
    for row in rows:
        employee_id = row['employee_id']
        month = row['month']
        day = row['day']
        attendance_records[employee_id][month][day] = True  # Mark as checked
    print (attendance_records)

    conn.close()

    return render_template('index.html', employees=employees,
                           months=months, days_in_month=days_in_month,
                           attendance_records=attendance_records)


# Route to handle adding an employee
@app.route('/add_employee', methods=['POST'])
def add_employee():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        contact = request.form['contact']

        # Add the employee to the database
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("INSERT INTO employees (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))


# Route to handle attendance submission
@app.route('/save_attendance', methods=['POST'])
def save_attendance():
    if request.method == 'POST':
        # Get data from the AJAX request
        data = request.json
        employee_id = data['employee_id']
        employee_name = data['employee_name']
        month = data['month']
        day = data['day']

        try:
            # Connect to SQLite database
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()

            print(employee_id, month, day)

            # Insert attendance record into the database
            c.execute("INSERT INTO attendance (employee_id, month, day) VALUES (?, ?, ?)",
                      (employee_id, month, day))

            # Commit changes and close connection
            conn.commit()
            conn.close()

            # Return success response
            return jsonify({'success': True}), 200
        except Exception as e:
            # Handle errors
            print("Error:", e)
            return jsonify({'success': False, 'error': str(e)}), 500


# Route to handle salary submission
@app.route('/save_salary', methods=['POST'])
def save_salary():
    if request.method == 'POST':
        # Get data from the form
        salary_date = request.form['salaryDate']
        employee_id = request.form['employee']
        advance = request.form['advance']

        try:
            # Connect to SQLite database
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()
            print("save_salary", salary_date, employee_id, advance)

            # Insert salary record into the database
            c.execute("INSERT INTO salary (date, employee_id, advance) VALUES (?, ?, ?)",
                      (salary_date, employee_id, advance))

            # Commit changes and close connection
            conn.commit()
            conn.close()

            # Return success response
            return jsonify({'success': True}), 200
        except Exception as e:
            # Handle errors
            print("Error:", e)
            return jsonify({'success': False, 'error': str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
