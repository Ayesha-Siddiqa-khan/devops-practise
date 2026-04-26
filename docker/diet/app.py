from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "diet.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-me")


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS meal_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_name TEXT NOT NULL,
            calories INTEGER NOT NULL CHECK(calories >= 0),
            protein REAL NOT NULL CHECK(protein >= 0),
            carbs REAL NOT NULL CHECK(carbs >= 0),
            fats REAL NOT NULL CHECK(fats >= 0),
            meal_time TEXT NOT NULL,
            consumed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    db.commit()


@app.teardown_appcontext
def close_db(_error: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/", methods=["GET"])
def index():
    init_db()
    db = get_db()
    entries = db.execute(
        """
        SELECT id, meal_name, calories, protein, carbs, fats, meal_time, consumed, created_at
        FROM meal_entries
        ORDER BY datetime(created_at) DESC
        """
    ).fetchall()

    totals = db.execute(
        """
        SELECT
            COALESCE(SUM(calories), 0) AS calories,
            COALESCE(SUM(protein), 0) AS protein,
            COALESCE(SUM(carbs), 0) AS carbs,
            COALESCE(SUM(fats), 0) AS fats
        FROM meal_entries
        """
    ).fetchone()

    consumed_count = db.execute(
        "SELECT COUNT(*) AS count FROM meal_entries WHERE consumed = 1"
    ).fetchone()["count"]

    return render_template(
        "index.html",
        entries=entries,
        totals=totals,
        consumed_count=consumed_count,
        entry_count=len(entries),
    )


@app.route("/add", methods=["POST"])
def add_entry():
    init_db()
    meal_name = request.form.get("meal_name", "").strip()
    meal_time = request.form.get("meal_time", "Other")

    if not meal_name:
        flash("Meal name is required.", "error")
        return redirect(url_for("index"))

    try:
        calories = int(request.form.get("calories", "0"))
        protein = float(request.form.get("protein", "0"))
        carbs = float(request.form.get("carbs", "0"))
        fats = float(request.form.get("fats", "0"))
    except ValueError:
        flash("Calories and macros must be valid numbers.", "error")
        return redirect(url_for("index"))

    if min(calories, protein, carbs, fats) < 0:
        flash("Calories and macros cannot be negative.", "error")
        return redirect(url_for("index"))

    db = get_db()
    db.execute(
        """
        INSERT INTO meal_entries (meal_name, calories, protein, carbs, fats, meal_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            meal_name,
            calories,
            protein,
            carbs,
            fats,
            meal_time,
            datetime.utcnow().isoformat(timespec="seconds"),
        ),
    )
    db.commit()
    flash("Meal added successfully.", "success")
    return redirect(url_for("index"))


@app.route("/toggle/<int:entry_id>", methods=["POST"])
def toggle_consumed(entry_id: int):
    init_db()
    db = get_db()
    row = db.execute(
        "SELECT consumed FROM meal_entries WHERE id = ?", (entry_id,)
    ).fetchone()

    if row is None:
        flash("Meal not found.", "error")
        return redirect(url_for("index"))

    new_value = 0 if row["consumed"] else 1
    db.execute("UPDATE meal_entries SET consumed = ? WHERE id = ?", (new_value, entry_id))
    db.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id: int):
    init_db()
    db = get_db()
    db.execute("DELETE FROM meal_entries WHERE id = ?", (entry_id,))
    db.commit()
    flash("Meal deleted.", "success")
    return redirect(url_for("index"))


@app.route("/clear", methods=["POST"])
def clear_all_entries():
    init_db()
    db = get_db()
    db.execute("DELETE FROM meal_entries")
    db.commit()
    flash("All meals cleared.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
