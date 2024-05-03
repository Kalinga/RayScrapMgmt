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
    c.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INTEGER PRIMARY KEY, name TEXT, contact TEXT)''')
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
    c = conn.cursor()
    c.execute("SELECT * FROM employees")
    employees = c.fetchall()
    conn.close()

    return render_template('index.html', employees=employees)


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


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
