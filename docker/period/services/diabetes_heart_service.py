from datetime import datetime, timedelta

from sqlalchemy import func

from models import HealthMetricLog, MealLog


def classify_meal(foods: str):
    text = (foods or "").lower()

    avoid_keywords = {
        "soda",
        "cola",
        "fried",
        "pastry",
        "cake",
        "candy",
        "chips",
        "processed meat",
        "high salt",
        "bacon",
    }
    moderate_keywords = {
        "white rice",
        "potato",
        "naan",
        "bread",
        "juice",
        "sweet yogurt",
    }

    if any(keyword in text for keyword in avoid_keywords):
        return "avoid", "This meal may raise sugar or blood pressure. Consider a lighter, low-salt and low-sugar alternative."
    if any(keyword in text for keyword in moderate_keywords):
        return "moderate", "This meal is okay in moderation. Pair with fiber, protein, and hydration."
    return "safe", "This looks heart-friendly and diabetes-supportive. Keep portions balanced."


def _series(logs):
    return [
        {
            "x": log.logged_at.strftime("%Y-%m-%d %H:%M"),
            "y1": log.value_primary,
            "y2": log.value_secondary,
            "context": log.context,
        }
        for log in logs
    ]


def build_insights(user_id):
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    glucose_logs = (
        HealthMetricLog.query.filter_by(user_id=user_id, metric_type="glucose")
        .filter(HealthMetricLog.logged_at >= seven_days_ago)
        .order_by(HealthMetricLog.logged_at.asc())
        .all()
    )

    bp_logs = (
        HealthMetricLog.query.filter_by(user_id=user_id, metric_type="blood_pressure")
        .filter(HealthMetricLog.logged_at >= seven_days_ago)
        .order_by(HealthMetricLog.logged_at.asc())
        .all()
    )

    weight_logs = (
        HealthMetricLog.query.filter_by(user_id=user_id, metric_type="weight")
        .filter(HealthMetricLog.logged_at >= seven_days_ago)
        .order_by(HealthMetricLog.logged_at.asc())
        .all()
    )

    activity_logs = (
        HealthMetricLog.query.filter_by(user_id=user_id, metric_type="activity")
        .filter(HealthMetricLog.logged_at >= seven_days_ago)
        .order_by(HealthMetricLog.logged_at.asc())
        .all()
    )

    alerts = []
    tips = []

    fasting_high = [log for log in glucose_logs if log.context == "fasting" and (log.value_primary or 0) >= 130]
    post_meal_spikes = [log for log in glucose_logs if log.context == "post_meal" and (log.value_primary or 0) >= 180]
    low_sugar = [log for log in glucose_logs if (log.value_primary or 0) < 70]

    if fasting_high:
        alerts.append(
            {
                "type": "warning",
                "message": "Fasting glucose has been high on multiple entries. Consider re-checking and discussing with your doctor.",
            }
        )

    if post_meal_spikes:
        alerts.append(
            {
                "type": "warning",
                "message": "Post-meal sugar spikes detected. Try smaller portions and low-sugar meals.",
            }
        )

    if low_sugar:
        alerts.append(
            {
                "type": "critical",
                "message": "Low glucose readings detected. Re-check levels and seek medical attention if symptoms persist.",
            }
        )

    high_bp = [
        log for log in bp_logs if (log.value_primary or 0) >= 140 or (log.value_secondary or 0) >= 90
    ]
    if high_bp:
        alerts.append(
            {
                "type": "critical",
                "message": "High blood pressure readings observed. Please re-check and seek medical advice if this continues.",
            }
        )

    avg_steps = 0
    if activity_logs:
        avg_steps = (sum((log.value_primary or 0) for log in activity_logs) / len(activity_logs))

    if avg_steps and avg_steps < 3000 and (post_meal_spikes or high_bp):
        tips.append("Lower activity and higher readings may be linked. A 15-20 minute walk after meals can help.")

    tips.extend(
        [
            "Stay hydrated with frequent water intake.",
            "Prioritize balanced meals: low sugar, low sodium, low saturated fat.",
            "Maintain sleep and stress-management routine.",
            "Avoid smoking and reduce excess salt/sugar.",
        ]
    )

    timeline_query = (
        HealthMetricLog.query.filter_by(user_id=user_id)
        .order_by(HealthMetricLog.logged_at.desc())
        .limit(40)
        .all()
    )
    timeline = [
        {
            "time": log.logged_at.strftime("%b %d, %Y %H:%M"),
            "metric": log.metric_type,
            "value": f"{log.value_primary or '-'} {log.unit or ''}".strip(),
            "extra": f"{log.value_secondary or ''}".strip(),
            "context": log.context or "",
        }
        for log in timeline_query
    ]

    return {
        "trends": {
            "glucose": _series(glucose_logs),
            "blood_pressure": _series(bp_logs),
            "weight": _series(weight_logs),
        },
        "alerts": alerts,
        "tips": tips,
        "timeline": timeline,
    }


def assistant_reply(question: str, insights: dict):
    text = (question or "").lower().strip()

    if not text:
        return "I am here with you. You can ask about sugar control, blood pressure, food choices, or daily routine support."

    if "meal" in text or "food" in text or "diet" in text:
        return "Try plate balance: half vegetables, quarter protein, quarter whole grains. Choose low-sugar and low-salt meals."

    if "bp" in text or "blood pressure" in text or "heart" in text:
        return "Track blood pressure regularly, reduce excess salt, and include daily walking. If high readings continue, consult your doctor."

    if "sugar" in text or "glucose" in text:
        return "Check fasting and post-meal patterns, hydrate well, and avoid sugary snacks. Re-check unusual readings for safety."

    if "exercise" in text or "walk" in text:
        return "A short walk after meals, light strength work, and consistent movement can support both sugar and heart health."

    if insights.get("alerts"):
        return "I noticed some warning patterns. Please re-check your levels and seek medical care if symptoms persist."

    return "You are doing a good job tracking your health. Keep logging daily, stay hydrated, and take one small healthy step at a time."
