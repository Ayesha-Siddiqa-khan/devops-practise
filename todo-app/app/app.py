# app.py

from flask import Flask, render_template, jsonify, request
from datetime import datetime
import os
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "todo-secret-key")

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "tododb")
DB_USER = os.environ.get("DB_USER", "todouser")
DB_PASS = os.environ.get("DB_PASS", "todopass")


def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=psycopg2.extras.RealDictCursor,
        connect_timeout=3
    )


def init_db():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                priority VARCHAR(10) DEFAULT 'medium',
                category VARCHAR(50) DEFAULT 'General',
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully")

    except Exception as e:
        print(f"DB init error: {e}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/todos", methods=["GET"])
def get_todos():
    try:
        filter_by = request.args.get("filter", "all")
        category = request.args.get("category", "")

        conn = get_db()
        cur = conn.cursor()

        query = "SELECT * FROM todos"
        conditions = []
        params = []

        if filter_by == "active":
            conditions.append("completed = FALSE")
        elif filter_by == "completed":
            conditions.append("completed = TRUE")

        if category:
            conditions.append("category = %s")
            params.append(category)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        cur.execute(query, params)
        todos = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify([dict(t) for t in todos])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/todos", methods=["POST"])
def create_todo():
    try:
        data = request.get_json()

        title = data.get("title", "").strip()
        if not title:
            return jsonify({"error": "Title is required"}), 400

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO todos (title, description, priority, category)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (
            title,
            data.get("description", ""),
            data.get("priority", "medium"),
            data.get("category", "General")
        ))

        todo = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return jsonify(dict(todo)), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    try:
        data = request.get_json()

        conn = get_db()
        cur = conn.cursor()

        fields = []
        params = []

        if "title" in data:
            fields.append("title = %s")
            params.append(data["title"])

        if "description" in data:
            fields.append("description = %s")
            params.append(data["description"])

        if "completed" in data:
            fields.append("completed = %s")
            params.append(data["completed"])

        if "priority" in data:
            fields.append("priority = %s")
            params.append(data["priority"])

        if "category" in data:
            fields.append("category = %s")
            params.append(data["category"])

        fields.append("updated_at = %s")
        params.append(datetime.utcnow())
        params.append(todo_id)

        cur.execute(
            f"UPDATE todos SET {', '.join(fields)} WHERE id = %s RETURNING *",
            params
        )

        todo = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        if not todo:
            return jsonify({"error": "Todo not found"}), 404

        return jsonify(dict(todo))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM todos WHERE id = %s RETURNING id",
            (todo_id,)
        )

        deleted = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        if not deleted:
            return jsonify({"error": "Todo not found"}), 404

        return jsonify({"message": "Deleted", "id": todo_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def get_stats():
    try:
        conn = get_db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) AS total FROM todos")
        total = cur.fetchone()["total"]

        cur.execute(
            "SELECT COUNT(*) AS completed FROM todos WHERE completed = TRUE"
        )
        completed = cur.fetchone()["completed"]

        cur.close()
        conn.close()

        return jsonify({
            "total": total,
            "completed": completed,
            "active": total - completed
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- HEALTH CHECKS ----------

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/ready")
def ready():
    try:
        conn = get_db()
        conn.close()
        return jsonify({"status": "ready"}), 200
    except Exception as e:
        return jsonify({
            "status": "not ready",
            "error": str(e)
        }), 500


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)