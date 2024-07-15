# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import date
import datetime


# Initialize Flask app
app = Flask(__name__)
app.template_folder = '../templates/'  # Configuring the template folder


# Function to create the SQLite database and tables
def create_tables():
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees 
                 (id INTEGER PRIMARY KEY,
                 salary INTEGER,
                 employee_name TEXT,
                 contact TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attendance
                 (id INTEGER PRIMARY KEY,
                 employee_id INTEGER, 
                 employee_name TEXT,
                 month INTEGER, 
                 day INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS salary
                 (id INTEGER PRIMARY KEY,
                 date TEXT,
                 employee_name TEXT, 
                 payment INTEGER)''')
    conn.commit()
    conn.close()


# Call function to create tables
create_tables()

# Dummy data for months and days (you can replace this with actual data)
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]

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
    "October": + 31,
    "November": 30,
    "December": 31
}

# Route to display the Admin tab
@app.route('/')
def index():
    # Fetch employees from the database
    conn = sqlite3.connect('employee.db')
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
                attendance_records[employee_id][month]['total'] = 0  # Initialize total days present to 0
                attendance_records[employee_id][month][day] = False  # Initialize as unchecked

    # Execute the query to fetch attendance records
    c.execute("SELECT employee_id, month, day FROM attendance")
    rows = c.fetchall()
    for row in rows:
        employee_id = row['employee_id']
        month = row['month']
        day = row['day']
        attendance_records[employee_id][month][day] = True  # Mark as checked
        attendance_records[employee_id][month]['total'] += 1  # Increment total days present

    print (attendance_records)

    conn.close()

    # Inside your route function
    today_date = date.today().isoformat()  # Get today's date in ISO format (YYYY-MM-DD)

    return render_template('index.html', employees=employees,
                           months=months, days_in_month=days_in_month,
                           attendance_records=attendance_records, today_date=today_date)


# Route to handle adding an employee
@app.route('/add_employee', methods=['POST'])
def add_employee():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name'].strip()
        contact = request.form['contact'].strip()
        salary = request.form['monthlysalary'].strip()

        # Add the employee to the database
        conn = sqlite3.connect('employee.db')
        c = conn.cursor()
        c.execute("INSERT INTO employees (employee_name, salary, contact) VALUES (?, ?, ?)", (name, salary, contact))
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
            conn = sqlite3.connect('employee.db')
            c = conn.cursor()

            print(employee_id, month, day)
            # Check if the record already exists
            c.execute("SELECT * FROM attendance WHERE employee_id = ? AND month = ? AND day = ?",
                      (employee_id, month, day))
            existing_record = c.fetchone()

            if existing_record:
                # If record exists, delete it
                c.execute("DELETE FROM attendance WHERE employee_id = ? AND month = ? AND day = ?",
                          (employee_id, month, day))
            else:
                # If record doesn't exist, insert it
                c.execute("INSERT INTO attendance (employee_id, employee_name, month, day) VALUES (?, ?, ?, ?)",
                      (employee_id, employee_name, month, day))

            # Commit changes and close connection
            conn.commit()
            conn.close()

            # Return success response
            return jsonify({'success': True}), 200
        except Exception as e:
            # Handle errors
            print("Error:", e)
            return jsonify({'success': False, 'error': str(e)}), 500

# Route to fetch salary information for the selected employee
@app.route('/get_salary', methods=['GET'])
def get_salary():
    # Get the selected employee from the request query parameters
    employee_name = request.args.get('employee')

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('employee.db')
        c = conn.cursor()
        # Get the current year and month
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        # Construct the start and end date strings for the current month
        start_date = f'{current_year}-{current_month:02d}-01'
        end_date = f'{current_year}-{current_month:02d}-31'  # Assuming 31 days in a month, adjust as needed


        # Query the database to retrieve salary information for the selected employee
        c.execute("SELECT date, payment FROM salary WHERE employee_name = ? AND date BETWEEN ? AND ?",
                  (employee_name, start_date, end_date))

        salary_data = c.fetchall()

        # Convert the fetched data into a list of dictionaries
        salary_info = [{'date': row[0], 'salary': row[1]} for row in salary_data]

        # Close the database connection
        conn.close()

        # Return the salary information as JSON response
        return jsonify(salary_info)

    except Exception as e:
        # Handle any errors that occur during database query
        return jsonify({'error': str(e)})

# Route to handle salary submission
@app.route('/save_salary', methods=['POST'])
def save_salary():
    if request.method == 'POST':
        # Get data from the form
        salary_date = request.form['salaryDate']
        employee_id = request.form['employee']
        payment = request.form['payment']

        try:
            # Connect to SQLite database
            conn = sqlite3.connect('employee.db')
            c = conn.cursor()
            print("save_salary", salary_date, employee_id, payment)

            # Insert salary record into the database
            c.execute("INSERT INTO salary (date, employee_name, payment) VALUES (?, ?, ?)",
                      (salary_date, employee_id, payment))

            # Commit changes and close connection
            conn.commit()
            conn.close()

            # Return success response
            return jsonify({'success': True}), 200
        except Exception as e:
            # Handle errors
            print("Error:", e)
            return jsonify({'success': False, 'error': str(e)}), 500



# Route to get the monthly details including the number of days worked for an employee
@app.route('/get_monthly_details', methods=['GET'])
def get_monthly_details():
    # Get the employee name from the request parameters
    employee_name = request.args.get('employee')

    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('employee.db')
        c = conn.cursor()

        # Get the current year and month
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month

        # Query the attendance table to count the number of days the employee worked in the current month
        c.execute("SELECT COUNT(*) FROM attendance WHERE employee_name = ? AND month = ?",
                  (employee_name, months[current_month-1]))
        days_worked = c.fetchone()[0]

        # Query the employees table to retrieve the salary of the specified employee
        c.execute("SELECT salary FROM employees WHERE employee_name = ?", (employee_name,))
        salary_record = c.fetchone()

        if salary_record:
            # If the employee exists, return the monthly salary and number of days worked as JSON response
            return jsonify({'employee_name': employee_name, 'monthly_salary': salary_record[0], 'days_worked': days_worked})
        else:
            # If the employee does not exist, return an error message
            return jsonify({'error': 'Employee not found'}), 404
    except Exception as e:
        # If any error occurs during database connection or query execution, return an error message
        return jsonify({'error': str(e)}), 500
    finally:
        # Close the database connection
        if 'conn' in locals():
            conn.close()
# Route to fetch payment records based on selected employee and month
@app.route('/fetch_payment_records', methods=['GET'])
def fetch_payment_records():
    employee_name = request.args.get('employee')
    month = int(request.args.get('month'))

    try:
        conn = sqlite3.connect('employee.db')
        c = conn.cursor()

        start_date = f'{datetime.datetime.now().year}-{month:02d}-01'
        end_date = f'{datetime.datetime.now().year}-{month:02d}-31'

        c.execute("SELECT date, payment FROM salary WHERE employee_name = ? AND date BETWEEN ? AND ?",
                  (employee_name, start_date, end_date))
        salary_data = c.fetchall()

        payment_records = [{'date': row[0], 'payment': row[1]} for row in salary_data]

        conn.close()

        return jsonify({'payment_records': payment_records})

    except Exception as e:
        return jsonify({'error': str(e)})

# Helper function to get all employees
def get_all_employees():
    conn = sqlite3.connect('employee.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM employees")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
