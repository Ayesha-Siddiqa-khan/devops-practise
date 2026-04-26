from flask import Flask, request, jsonify, render_template
from datetime import datetime, date
import time
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)

def get_db_connection(retries=10, delay=2):
    for _ in range(retries):
        try:
            conn = psycopg2.connect(
                host="db",
                database="age_db",
                user="postgres",
                password="postgres"
            )
            return conn
        except OperationalError:
            time.sleep(delay)

    raise OperationalError("Could not connect to database after multiple attempts")


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            dob DATE NOT NULL,
            age INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()

    cur.close()
    conn.close()


def calculate_age_from_dob(dob_text):
    birth_date = datetime.strptime(dob_text, "%Y-%m-%d").date()
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return birth_date, age

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate_age():
    data = request.get_json(silent=True) or {}
    dob = data.get("dob", "").strip()

    if not dob:
        return jsonify({"error": "Date of birth is required. Use format YYYY-MM-DD."}), 400

    try:
        birth_date, age = calculate_age_from_dob(dob)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    if birth_date > date.today():
        return jsonify({"error": "Date of birth cannot be in the future."}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("INSERT INTO users (dob, age) VALUES (%s, %s)", (birth_date, age))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"age": age, "dob": dob})


@app.route("/history", methods=["GET"])
def history():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT dob, age, created_at
        FROM users
        ORDER BY id DESC
        LIMIT 10
        """
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    items = [
        {
            "dob": row[0].isoformat(),
            "age": row[1],
            "created_at": row[2].isoformat(sep=" ", timespec="seconds")
        }
        for row in rows
    ]

    return jsonify(items)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)