from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from models import HealthMetricLog, MealLog, MedicationLog, db
from services.diabetes_heart_service import assistant_reply, build_insights, classify_meal


diabetes_heart_bp = Blueprint("diabetes_heart", __name__)


@diabetes_heart_bp.route("/diabetes-heart")
@login_required
def diabetes_heart_page():
    return render_template("diabetes_heart.html", active_page="diabetes_heart")


@diabetes_heart_bp.route("/api/diabetes/log", methods=["POST"])
@login_required
def diabetes_log_api():
    payload = request.get_json(silent=True) or {}

    reading_type = str(payload.get("reading_type", "fasting")).strip()
    value = payload.get("value")

    try:
        value = float(value)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid glucose value."}), 400

    row = HealthMetricLog(
        user_id=current_user.id,
        metric_type="glucose",
        value_primary=value,
        unit="mg/dL",
        context=reading_type,
        payload=payload,
        logged_at=datetime.utcnow(),
    )
    db.session.add(row)
    db.session.commit()

    return jsonify({"message": "Glucose log saved.", "entry": row.to_dict()})


@diabetes_heart_bp.route("/api/heart/metrics", methods=["POST"])
@login_required
def heart_metrics_api():
    payload = request.get_json(silent=True) or {}
    metric_type = str(payload.get("metric_type", "blood_pressure")).strip()

    if metric_type not in {"blood_pressure", "heart_rate", "weight", "activity"}:
        return jsonify({"error": "Invalid metric type."}), 400

    if metric_type == "blood_pressure":
        try:
            systolic = float(payload.get("systolic"))
            diastolic = float(payload.get("diastolic"))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid blood pressure values."}), 400

        row = HealthMetricLog(
            user_id=current_user.id,
            metric_type=metric_type,
            value_primary=systolic,
            value_secondary=diastolic,
            unit="mmHg",
            context="resting",
            payload=payload,
        )
    else:
        try:
            value = float(payload.get("value"))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid metric value."}), 400

        units = {
            "heart_rate": "bpm",
            "weight": "kg",
            "activity": "steps",
        }
        row = HealthMetricLog(
            user_id=current_user.id,
            metric_type=metric_type,
            value_primary=value,
            unit=units.get(metric_type),
            context=str(payload.get("context", "daily")),
            payload=payload,
        )

    db.session.add(row)
    db.session.commit()

    return jsonify({"message": "Metric saved.", "entry": row.to_dict()})


@diabetes_heart_bp.route("/api/meal/log", methods=["POST"])
@login_required
def meal_log_api():
    payload = request.get_json(silent=True) or {}
    meal_type = str(payload.get("meal_type", "meal")).strip()
    foods = str(payload.get("foods", "")).strip()

    if not foods:
        return jsonify({"error": "Foods are required."}), 400

    classification, guidance = classify_meal(foods)
    row = MealLog(
        user_id=current_user.id,
        meal_type=meal_type,
        foods=foods,
        classification=classification,
        guidance=guidance,
    )
    db.session.add(row)
    db.session.commit()

    return jsonify({"message": "Meal log saved.", "entry": row.to_dict()})


@diabetes_heart_bp.route("/api/medication/log", methods=["POST"])
@login_required
def medication_log_api():
    payload = request.get_json(silent=True) or {}
    medicine_name = str(payload.get("medicine_name", "")).strip()

    if not medicine_name:
        return jsonify({"error": "Medicine name is required."}), 400

    row = MedicationLog(
        user_id=current_user.id,
        medicine_name=medicine_name,
        dosage=str(payload.get("dosage", "")).strip(),
        schedule_time=str(payload.get("schedule_time", "")).strip(),
        reminder_enabled=bool(payload.get("reminder_enabled", True)),
        notes=str(payload.get("notes", "")).strip(),
    )
    db.session.add(row)
    db.session.commit()

    return jsonify({"message": "Medication reminder saved.", "entry": row.to_dict()})


@diabetes_heart_bp.route("/api/insights", methods=["GET"])
@login_required
def insights_api():
    return jsonify(build_insights(current_user.id))


@diabetes_heart_bp.route("/api/assistant/query", methods=["POST"])
@login_required
def assistant_query_api():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()

    insights = build_insights(current_user.id)
    reply = assistant_reply(question, insights)

    return jsonify(
        {
            "reply": reply,
            "disclaimer": "This assistant gives educational support only and does not replace professional medical advice.",
        }
    )
