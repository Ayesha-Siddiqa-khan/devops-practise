from datetime import date, datetime

import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)

conn = psycopg2.connect(
    host="age_db",
    database="mydb",
    user="myuser",
    password="mypass"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    age INT
);
""")
conn.commit()


def calculate_age_parts(dob: date, today: date) -> tuple[int, int, int]:
    """Return age as (years, months, days)."""
    years = today.year - dob.year
    months = today.month - dob.month
    days = today.day - dob.day

    if days < 0:
        months -= 1
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year

        if prev_month == 12:
            next_month = date(prev_year + 1, 1, 1)
        else:
            next_month = date(prev_year, prev_month + 1, 1)

        first_of_prev = date(prev_year, prev_month, 1)
        days_in_prev_month = (next_month - first_of_prev).days
        days += days_in_prev_month

    if months < 0:
        years -= 1
        months += 12

    return years, months, days


def next_birthday_days(dob: date, today: date) -> int:
    """Return number of days until the next birthday."""
    try:
        next_bday = date(today.year, dob.month, dob.day)
    except ValueError:
        # Handle Feb 29 birthday in non-leap years.
        next_bday = date(today.year, 3, 1)

    if next_bday < today:
        try:
            next_bday = date(today.year + 1, dob.month, dob.day)
        except ValueError:
            next_bday = date(today.year + 1, 3, 1)

    return (next_bday - today).days


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    dob_input = ""

    if request.method == "POST":
        dob_input = request.form.get("dob", "").strip()

        if not dob_input:
            error = "Please select your date of birth."
        else:
            try:
                dob = datetime.strptime(dob_input, "%Y-%m-%d").date()
                today = date.today()

                if dob > today:
                    error = "Date of birth cannot be in the future."
                else:
                    years, months, days = calculate_age_parts(dob, today)
                    result = {
                        "years": years,
                        "months": months,
                        "days": days,
                        "next_birthday_days": next_birthday_days(dob, today),
                    }
            except ValueError:
                error = "Invalid date format. Please use YYYY-MM-DD."

    return render_template(
        "index.html",
        result=result,
        error=error,
        dob_input=dob_input,
        now=date.today().isoformat(),
    )


@app.route("/add/<name>/<int:age>")
def add_user(name, age):
    cursor.execute(
        "INSERT INTO users (name, age) VALUES (%s, %s)",
        (name, age)
    )
    conn.commit()
    return f"User {name} added!"


@app.route("/users")
def get_users():
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    return str(users)


@app.route("/age/<int:year>")
def calculate_age(year):
    current_year = datetime.now().year
    age = current_year - year

    cursor.execute(
        "INSERT INTO users (name, age) VALUES (%s, %s)",
        ("User", age)
    )
    conn.commit()

    return f"Your age is {age}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
