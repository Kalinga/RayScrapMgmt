# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for
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
                 (id INTEGER PRIMARY KEY, employee_id INTEGER, check_in TEXT, check_out TEXT)''')
    conn.commit()
    conn.close()


# Call function to create tables
create_tables()


# Route to display the Admin tab
@app.route('/')
def index():
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
    conn.close()

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
        "October": 31,
        "November": 30,
        "December": 31
    }
    return render_template('index.html', employees=employees, months=months, days_in_month=days_in_month)


# Route to handle adding an employee
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
@app.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    if request.method == 'POST':
        # Parse attendance data from the form
        employee_id = request.form['employee_id']
        month = request.form['month']
        day = request.form['day']
        attendance_status = request.form['attendance_status']  # Assuming this is how you track attendance

        try:
            # Connect to SQLite database
            conn = sqlite3.connect('attendance.db')
            c = conn.cursor()

            # Insert attendance data into the database
            c.execute("INSERT INTO attendance (employee_id, month, day, attendance_status) VALUES (?, ?, ?, ?)",
                      (employee_id, month, day, attendance_status))

            # Commit changes and close connection
            conn.commit()
            conn.close()

            # Redirect to a success page or display a success message
            return redirect(url_for('success'))
        except Exception as e:
            # Handle errors
            print("Error:", e)
            return "An error occurred while submitting attendance."


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
