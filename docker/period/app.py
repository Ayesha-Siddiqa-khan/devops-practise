import os
import re
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from models import HealthMetricLog, HealthModule, MealLog, User, WorkoutCompletion, WorkoutPlan, db
from routes import diabetes_heart_bp
from services.breast_mental_service import (
    assess_breast_health,
    assess_mental_wellness,
    check_mental_emergency_text,
    get_breast_self_exam_steps,
)
from services.fitness_diet_service import generate_fitness_diet_plan
from services.labor_emergency_service import (
    assess_labor_emergency,
    assess_postpartum_warning,
    smart_emergency_response,
)
from services.leucorrhea_service import evaluate_leucorrhea
from services.period_service import calculate_cycle_predictions, validate_cycle_input
from services.pregnancy_service import get_pregnancy_month_details
from services.risk_service import assess_pregnancy_risk
from services.mood_chat_service import generate_chat_reply
from services.symptom_nlp_service import analyze_free_text_symptoms
from services.thyroid_service import assess_thyroid_awareness
from services.tips_service import generate_daily_smart_tips
from services.workout_service import generate_daily_workout_plan
from services.women_health_service import analyze_women_problem

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-this")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///femcare.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.register_blueprint(diabetes_heart_bp)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def _slugify(value: str):
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-")


def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)

    return wrapper


def seed_modules():
    defaults = [
        {
            "title": "Period Tracker",
            "description": "Track next period date, ovulation, and fertile window.",
            "category": "period",
            "route": "period-tracker",
            "icon": "fa-calendar-days",
            "target_url": "/period",
        },
        {
            "title": "Pregnancy Guide",
            "description": "Month-by-month pregnancy insights and safe guidance.",
            "category": "pregnancy",
            "route": "pregnancy-guide",
            "icon": "fa-baby",
            "target_url": "/pregnancy",
        },
        {
            "title": "Women Health Checkers",
            "description": "Breast, thyroid, mental wellness, and symptom awareness tools.",
            "category": "women_health",
            "route": "women-health-checkers",
            "icon": "fa-stethoscope",
            "target_url": "/health",
        },
        {
            "title": "Fitness & Diet Planner",
            "description": "Goal-based diet and fitness planning with condition-aware tips.",
            "category": "fitness",
            "route": "fitness-diet-planner",
            "icon": "fa-dumbbell",
            "target_url": "/fitness",
        },
        {
            "title": "Workout Trainer",
            "description": "Visual workout cards, timer, and streak tracking.",
            "category": "fitness",
            "route": "workout-trainer",
            "icon": "fa-person-running",
            "target_url": "/workout",
        },
        {
            "title": "Daily Smart Tips",
            "description": "Daily cycle and hygiene care reminders.",
            "category": "women_health",
            "route": "daily-smart-tips",
            "icon": "fa-lightbulb",
            "target_url": "/tips",
        },
        {
            "title": "Mood Checker Chatbot",
            "description": "Safe emotional support chat for stress, sadness, anxiety, and reflection.",
            "category": "mental_health",
            "route": "mood-checker-chatbot",
            "icon": "fa-comments",
            "target_url": "/mood-chat",
        },
        {
            "title": "Diabetes & Heart Health",
            "description": "Track glucose, blood pressure, heart rate, meals, medicines, and get safety insights.",
            "category": "disease",
            "route": "diabetes-heart-health",
            "icon": "fa-heart-pulse",
            "target_url": "/diabetes-heart",
        },
    ]

    changed = False
    for item in defaults:
        existing = HealthModule.query.filter_by(route=item["route"]).first()
        if not existing:
            db.session.add(HealthModule(status="active", **item))
            changed = True
        else:
            # Keep existing admin edits, but ensure defaults remain reachable.
            if not existing.target_url and item.get("target_url"):
                existing.target_url = item["target_url"]
                changed = True

    if changed:
        db.session.commit()


def seed_admin():
    if User.query.filter_by(is_admin=True).first():
        return

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@femcare.ai")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    admin = User(
        username=admin_username,
        email=admin_email,
        password_hash=generate_password_hash(admin_password),
        is_admin=True,
    )
    db.session.add(admin)
    db.session.commit()


def _normalize_workout_input(payload):
    form = {
        "age": str(payload.get("age", "")).strip(),
        "fitness_level": str(payload.get("fitness_level", "beginner")).strip() or "beginner",
        "goal": str(payload.get("goal", "fitness")).strip() or "fitness",
        "activity_level": str(payload.get("activity_level", "low")).strip() or "low",
        "cycle_phase": str(payload.get("cycle_phase", "regular")).strip() or "regular",
        "thyroid": "yes" if payload.get("thyroid") in {"yes", True, "true", "on", 1, "1"} else "no",
        "pcos": "yes" if payload.get("pcos") in {"yes", True, "true", "on", 1, "1"} else "no",
        "pregnancy": "yes" if payload.get("pregnancy") in {"yes", True, "true", "on", 1, "1"} else "no",
    }

    errors = []
    try:
        age = int(form["age"])
        if age < 13 or age > 60:
            errors.append("Age should be between 13 and 60 for this planner.")
    except ValueError:
        age = 0
        errors.append("Please enter a valid age.")

    if form["fitness_level"] not in {"beginner", "intermediate", "advanced"}:
        errors.append("Invalid fitness level.")
    if form["goal"] not in {"fitness", "weight_loss", "weight_gain", "pregnancy_safe"}:
        errors.append("Invalid workout goal.")
    if form["activity_level"] not in {"low", "medium", "high"}:
        errors.append("Invalid activity level.")
    if form["cycle_phase"] not in {"regular", "period", "ovulation", "late_luteal"}:
        errors.append("Invalid cycle phase.")

    return form, age, errors


def _calculate_workout_streak(user_id):
    rows = (
        db.session.query(func.date(WorkoutCompletion.completed_at))
        .filter(WorkoutCompletion.user_id == user_id)
        .distinct()
        .order_by(func.date(WorkoutCompletion.completed_at).desc())
        .all()
    )

    if not rows:
        return 0

    def _as_date(value):
        if isinstance(value, date):
            return value
        return datetime.fromisoformat(str(value)).date()

    unique_dates = [_as_date(item[0]) for item in rows if item and item[0]]
    if not unique_dates:
        return 0

    streak = 1
    cursor = unique_dates[0]
    for check_date in unique_dates[1:]:
        if check_date == cursor - timedelta(days=1):
            streak += 1
            cursor = check_date
        else:
            break
    return streak


def _persist_workout_plan(user_id, form, age, plan_payload):
    record = WorkoutPlan(
        user_id=user_id,
        age=age,
        fitness_level=form["fitness_level"],
        goal=form["goal"],
        activity_level=form["activity_level"],
        cycle_phase=form["cycle_phase"],
        thyroid=form["thyroid"] == "yes",
        pcos=form["pcos"] == "yes",
        pregnancy=form["pregnancy"] == "yes",
        plan_payload=plan_payload,
    )
    db.session.add(record)
    db.session.commit()
    return record


def _get_plan_completion_keys(user_id, plan_id):
    rows = WorkoutCompletion.query.filter_by(user_id=user_id, plan_id=plan_id).all()
    return [row.exercise_key for row in rows]


def _get_time_bucket(hour_value):
    if 5 <= hour_value < 12:
        return "Morning"
    if 12 <= hour_value < 17:
        return "Afternoon"
    return "Evening"


def _score_mood_text(text):
    lowered = (text or "").lower()
    if any(token in lowered for token in {"panic", "hopeless", "crying", "overwhelmed", "anxious", "anxiety"}):
        return 2
    if any(token in lowered for token in {"sad", "tired", "low", "stressed", "stress", "angry"}):
        return 4
    if any(token in lowered for token in {"calm", "okay", "fine", "better", "grateful", "happy"}):
        return 7
    return 5


def _build_dashboard_summary(user):
    now_local = datetime.now()
    greeting = f"Good {_get_time_bucket(now_local.hour)}"

    cycle_profile = session.get("cycle_profile") or {}
    cycle_phase = "Awaiting cycle input"
    next_period_date = "Add period data"
    ovulation_window = "Will appear after cycle update"
    cycle_timeline = []
    cycle_day = None

    stored_last_period = str(cycle_profile.get("last_period_date", "")).strip()
    stored_cycle_length = cycle_profile.get("cycle_length")
    if stored_last_period and stored_cycle_length:
        try:
            parsed_date = datetime.strptime(stored_last_period, "%Y-%m-%d").date()
            cycle_length = int(stored_cycle_length)
            cycle_data = calculate_cycle_predictions(parsed_date, cycle_length)
            next_period_date = cycle_data["next_period"]
            ovulation_window = cycle_data["fertile_window"]
            cycle_timeline = cycle_data.get("timeline", [])[:5]

            raw_day = (date.today() - parsed_date).days
            cycle_day = (raw_day % cycle_length) + 1 if raw_day >= 0 else 1

            if cycle_day <= 5:
                cycle_phase = "Menstrual phase"
            elif cycle_day <= 13:
                cycle_phase = "Follicular phase"
            elif cycle_day <= 16:
                cycle_phase = "Ovulation window"
            else:
                cycle_phase = "Luteal phase"
        except (TypeError, ValueError):
            cycle_phase = "Awaiting cycle input"

    mood_history = [
        row for row in session.get("mood_chat_history", []) if isinstance(row, dict) and row.get("role") == "user"
    ]
    recent_mood_entries = mood_history[-7:]
    mood_points = []
    for idx, row in enumerate(recent_mood_entries, start=1):
        mood_points.append({"label": f"D{idx}", "score": _score_mood_text(row.get("text", ""))})

    if not mood_points:
        fallback = {"anxious": 3, "stressed": 4, "sad": 3, "calm": 7, "positive": 8}
        last_mood = str(session.get("mood_chat_last_mood", "calm")).strip().lower()
        mood_points = [{"label": "D1", "score": fallback.get(last_mood, 6)}]

    avg_mood = sum(item["score"] for item in mood_points) / len(mood_points)
    if avg_mood >= 7:
        mood_status = "Steady and positive"
    elif avg_mood >= 5:
        mood_status = "Balanced with mild stress"
    else:
        mood_status = "Needs extra care today"

    recent_activity = (
        HealthMetricLog.query.filter_by(user_id=user.id, metric_type="activity")
        .order_by(HealthMetricLog.logged_at.desc())
        .limit(7)
        .all()
    )
    avg_steps = 0
    if recent_activity:
        avg_steps = int(sum((entry.value_primary or 0) for entry in recent_activity) / len(recent_activity))

    if avg_steps >= 8000:
        energy_level = "High energy"
    elif avg_steps >= 5000:
        energy_level = "Moderate energy"
    else:
        energy_level = "Low energy"

    hydration_target_ml = 2400
    hydration_today_ml = min(hydration_target_ml, 1200 + int(avg_steps * 0.07)) if avg_steps else 1300

    latest_plan = WorkoutPlan.query.filter_by(user_id=user.id).order_by(WorkoutPlan.created_at.desc()).first()
    workout_completed = 0
    workout_total = 0
    workout_percent = 0
    if latest_plan:
        completed_keys = _get_plan_completion_keys(user.id, latest_plan.id)
        workout_completed = len(completed_keys)
        workout_total = len((latest_plan.plan_payload or {}).get("all_exercises", []))
        if workout_total > 0:
            workout_percent = round((workout_completed / workout_total) * 100)

    meal_rows = MealLog.query.filter_by(user_id=user.id).order_by(MealLog.logged_at.desc()).limit(10).all()
    avoid_count = len([row for row in meal_rows if row.classification == "avoid"])
    safe_count = len([row for row in meal_rows if row.classification == "safe"])

    recommendations = [
        "You are doing your best. One gentle healthy step today is enough.",
        "Try a 5-minute breathing pause and shoulder stretch between tasks.",
    ]
    if avoid_count > safe_count:
        recommendations.append("Aim for one low-salt, high-fiber meal in your next meal slot.")
    if avg_mood < 5:
        recommendations.append("Your mood trend looks heavy. Reach out to a trusted person and rest when possible.")
    if energy_level == "Low energy":
        recommendations.append("A short 10-minute walk can boost energy and reduce stress.")

    tip_context = generate_daily_smart_tips(str(cycle_day or ""), "")
    daily_tip = (tip_context.get("tips") or ["Hydrate and rest; your body responds best to steady care."])[0]

    completion_checks = [
        bool(stored_last_period),
        bool(mood_history),
        bool(latest_plan),
        bool(recent_activity),
    ]
    onboarding_percent = int((sum(1 for item in completion_checks if item) / len(completion_checks)) * 100)

    return {
        "user": {
            "name": user.username,
            "greeting": greeting,
            "headline": f"{greeting}, {user.username}",
        },
        "insights": {
            "cycle_phase": cycle_phase,
            "mood_status": mood_status,
            "energy_level": energy_level,
        },
        "widgets": {
            "next_period_date": next_period_date,
            "ovulation_window": ovulation_window,
            "mood_points": mood_points,
            "workout": {
                "completed": workout_completed,
                "total": workout_total,
                "progress_percent": workout_percent,
                "streak": _calculate_workout_streak(user.id),
            },
            "hydration": {
                "today_ml": hydration_today_ml,
                "target_ml": hydration_target_ml,
                "remaining_ml": max(hydration_target_ml - hydration_today_ml, 0),
            },
            "daily_tip": daily_tip,
            "recommendations": recommendations[:4],
        },
        "cycle_timeline": cycle_timeline,
        "onboarding": {
            "completion_percent": onboarding_percent,
            "tips": [
                "Add your latest period date to unlock cycle forecasting.",
                "Use mood chat once daily to improve personalized emotional insights.",
                "Track at least one workout routine to unlock progress recommendations.",
            ],
        },
    }


with app.app_context():
    db.create_all()
    seed_modules()
    seed_admin()


@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", active_page="dashboard")


@app.route("/api/modules")
@login_required
def modules_api():
    category = request.args.get("category", "").strip().lower()
    query = request.args.get("q", "").strip().lower()

    modules_query = HealthModule.query.filter_by(status="active")

    if category and category != "all":
        modules_query = modules_query.filter(HealthModule.category.ilike(category))

    if query:
        like_query = f"%{query}%"
        modules_query = modules_query.filter(
            (HealthModule.title.ilike(like_query)) | (HealthModule.description.ilike(like_query))
        )

    modules = modules_query.order_by(HealthModule.created_at.desc()).all()
    return jsonify({"modules": [module.to_dict() for module in modules]})


@app.route("/api/dashboard/summary")
@login_required
def dashboard_summary_api():
    return jsonify(_build_dashboard_summary(current_user))


@app.route("/module/<module_route>")
@login_required
def module_page(module_route):
    module = HealthModule.query.filter_by(route=module_route, status="active").first_or_404()
    return render_template("module_detail.html", active_page="dashboard", module=module)


@app.route("/mood-chat")
@login_required
def mood_chat_page():
    if "mood_chat_history" not in session:
        session["mood_chat_history"] = []
    return render_template("mood_chat.html", active_page="mood_chat")


@app.route("/chat", methods=["POST"])
@login_required
def mood_chat_api():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get("message", "")).strip()

    history = session.get("mood_chat_history", [])
    model_result = generate_chat_reply(message, history)

    if message:
        history.append({"role": "user", "text": message})
    history.append({"role": "assistant", "text": model_result["reply"]})

    session["mood_chat_history"] = history[-12:]
    session["mood_chat_last_mood"] = model_result.get("mood", "calm")
    session.modified = True

    return jsonify(
        {
            "reply": model_result["reply"],
            "mood": model_result["mood"],
            "intent": model_result.get("intent", "general_conversation"),
            "topic": model_result.get("topic", "general"),
            "urgent": model_result["urgent"],
            "disclaimer": "This support chat is educational and not a medical diagnosis.",
        }
    )


@app.route("/chat/history", methods=["GET"])
@login_required
def mood_chat_history_api():
    history = session.get("mood_chat_history", [])
    return jsonify({"messages": history})


@app.route("/chat/reset", methods=["POST"])
@login_required
def mood_chat_reset_api():
    session["mood_chat_history"] = []
    session.modified = True
    return jsonify({"message": "Chat history cleared."})


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already exists.", "error")
        else:
            user = User(username=username, email=email, password_hash=generate_password_hash(password), is_admin=False)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("auth_register.html", active_page="auth")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter((User.username == identifier) | (User.email == identifier.lower())).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid credentials.", "error")
        else:
            login_user(user)
            return redirect(url_for("dashboard"))

    return render_template("auth_login.html", active_page="auth")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/admin/modules")
@admin_required
def admin_modules():
    modules = HealthModule.query.order_by(HealthModule.created_at.desc()).all()
    return render_template("admin_modules.html", active_page="admin", modules=modules)


@app.route("/admin/modules/new", methods=["GET", "POST"])
@admin_required
def admin_modules_new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "women_health").strip().lower()
        route = _slugify(request.form.get("route", "").strip() or title)
        status = request.form.get("status", "active")
        icon = request.form.get("icon", "fa-heart")
        target_url = request.form.get("target_url", "").strip() or None

        if not title or not description or not route:
            flash("Title, description, and route are required.", "error")
        elif HealthModule.query.filter_by(route=route).first():
            flash("Route already exists. Choose another.", "error")
        else:
            module = HealthModule(
                title=title,
                description=description,
                category=category,
                route=route,
                status=status,
                icon=icon,
                target_url=target_url,
            )
            db.session.add(module)
            db.session.commit()
            flash("Module created successfully.", "success")
            return redirect(url_for("admin_modules"))

    return render_template("admin_module_form.html", active_page="admin", module=None)


@app.route("/admin/modules/<int:module_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_modules_edit(module_id):
    module = HealthModule.query.get_or_404(module_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "women_health").strip().lower()
        route = _slugify(request.form.get("route", "").strip() or title)

        if HealthModule.query.filter(HealthModule.route == route, HealthModule.id != module.id).first():
            flash("Route already exists. Choose another.", "error")
        else:
            module.title = title
            module.description = description
            module.category = category
            module.route = route
            module.status = request.form.get("status", "active")
            module.icon = request.form.get("icon", "fa-heart")
            module.target_url = request.form.get("target_url", "").strip() or None
            db.session.commit()
            flash("Module updated successfully.", "success")
            return redirect(url_for("admin_modules"))

    return render_template("admin_module_form.html", active_page="admin", module=module)


@app.route("/admin/modules/<int:module_id>/delete", methods=["POST"])
@admin_required
def admin_modules_delete(module_id):
    module = HealthModule.query.get_or_404(module_id)
    db.session.delete(module)
    db.session.commit()
    flash("Module deleted.", "success")
    return redirect(url_for("admin_modules"))


@app.route("/period", methods=["GET", "POST"])
@login_required
def period_tracker():
    errors = []
    result = None
    form = {"last_period_date": "", "cycle_length": ""}

    if request.method == "POST":
        form["last_period_date"] = request.form.get("last_period_date", "").strip()
        form["cycle_length"] = request.form.get("cycle_length", "").strip()
        errors, parsed_date, cycle_length = validate_cycle_input(form["last_period_date"], form["cycle_length"])

        if not errors:
            result = calculate_cycle_predictions(parsed_date, cycle_length)
            session["cycle_profile"] = {
                "last_period_date": parsed_date.isoformat(),
                "cycle_length": cycle_length,
            }
            session.modified = True

    return render_template(
        "period_tracker.html",
        active_page="period",
        errors=errors,
        result=result,
        form=form,
        today=date.today().isoformat(),
    )


@app.route("/pregnancy", methods=["GET", "POST"])
@login_required
def pregnancy_tracker():
    errors = []
    month_details = None
    selected_month = ""

    if request.method == "POST":
        selected_month = request.form.get("pregnancy_month", "").strip()
        if not selected_month:
            errors.append("Please select a pregnancy month.")
        else:
            try:
                month_number = int(selected_month)
                if month_number < 1 or month_number > 9:
                    errors.append("Pregnancy month must be between 1 and 9.")
                else:
                    month_details = get_pregnancy_month_details(month_number)
            except ValueError:
                errors.append("Invalid pregnancy month value.")

    return render_template(
        "pregnancy_tracker.html",
        active_page="pregnancy",
        errors=errors,
        month_details=month_details,
        selected_month=selected_month,
    )


@app.route("/health", methods=["GET", "POST"])
@login_required
def health_checker():
    errors = []
    risk_result = None
    leucorrhea_result = None
    problem_result = None
    symptom_result = None
    labor_result = None
    postpartum_result = None
    smart_response_result = None
    breast_result = None
    mental_result = None
    mental_emergency_result = None
    thyroid_result = None
    breast_self_steps = get_breast_self_exam_steps()
    action = request.form.get("action", "") if request.method == "POST" else ""

    if request.method == "POST":
        try:
            if action == "risk_checker":
                risk_result = assess_pregnancy_risk(
                    request.form.get("high_bp", "no"),
                    request.form.get("bleeding", "no"),
                    request.form.get("diabetes", "no"),
                    request.form.get("pain_level", "low"),
                )

            elif action == "leucorrhea_checker":
                leucorrhea_result = evaluate_leucorrhea(
                    request.form.get("color", "clear"),
                    request.form.get("smell", "none"),
                    request.form.get("itching", "no"),
                )

            elif action == "women_problem_checker":
                problem_key = request.form.get("problem_key", "")
                if not problem_key:
                    errors.append("Please select a women health problem type.")
                else:
                    problem_result = analyze_women_problem(problem_key)

            elif action == "symptom_nlp_checker":
                symptom_text = request.form.get("symptom_text", "")
                symptom_result = analyze_free_text_symptoms(symptom_text)

            elif action == "labor_emergency_checker":
                labor_result = assess_labor_emergency(
                    request.form.get("water_broken", "no"),
                    request.form.get("fluid_color", "clear"),
                    request.form.get("bad_smell", "no"),
                    request.form.get("fever", "no"),
                    request.form.get("baby_movement", "normal"),
                )

            elif action == "postpartum_checker":
                postpartum_flags = {
                    "heavy_bleeding": request.form.get("heavy_bleeding", "no"),
                    "high_fever": request.form.get("high_fever", "no"),
                    "severe_abdominal_pain": request.form.get("severe_abdominal_pain", "no"),
                    "foul_discharge": request.form.get("foul_discharge", "no"),
                    "extreme_sadness": request.form.get("extreme_sadness", "no"),
                }
                postpartum_result = assess_postpartum_warning(postpartum_flags)

            elif action == "smart_emergency_response":
                user_text = request.form.get("smart_text", "")
                smart_response_result = smart_emergency_response(user_text)

            elif action == "breast_health_checker":
                breast_result = assess_breast_health(
                    request.form.get("breast_lump", "no"),
                    request.form.get("breast_pain", "no"),
                    request.form.get("nipple_discharge", "no"),
                    request.form.get("skin_changes", "no"),
                )

            elif action == "mental_health_checker":
                mental_result = assess_mental_wellness(
                    request.form.get("mood", "neutral"),
                    request.form.get("sleep_issues", "no"),
                    request.form.get("stress_level", "low"),
                    request.form.get("daily_interest", "normal"),
                )

            elif action == "mental_emergency_text":
                mental_text = request.form.get("mental_text", "")
                mental_emergency_result = check_mental_emergency_text(mental_text)

            elif action == "thyroid_checker":
                thyroid_result = assess_thyroid_awareness(
                    request.form.get("weight_change", "none"),
                    request.form.get("fatigue", "no"),
                    request.form.get("hair_fall", "no"),
                    request.form.get("temp_sensitivity", "none"),
                    request.form.get("thyroid_irregular_periods", "no"),
                )

        except Exception:
            errors.append("Something went wrong while processing your request. Please try again.")

    return render_template(
        "health_checker.html",
        active_page="health",
        errors=errors,
        risk_result=risk_result,
        leucorrhea_result=leucorrhea_result,
        problem_result=problem_result,
        symptom_result=symptom_result,
        labor_result=labor_result,
        postpartum_result=postpartum_result,
        smart_response_result=smart_response_result,
        breast_result=breast_result,
        mental_result=mental_result,
        mental_emergency_result=mental_emergency_result,
        thyroid_result=thyroid_result,
        breast_self_steps=breast_self_steps,
        action=action,
    )


@app.route("/tips", methods=["GET", "POST"])
@login_required
def tips():
    tips_result = generate_daily_smart_tips("", "")
    form = {"cycle_day": "", "pregnancy_month": ""}

    if request.method == "POST":
        form["cycle_day"] = request.form.get("cycle_day", "").strip()
        form["pregnancy_month"] = request.form.get("pregnancy_month", "").strip()
        tips_result = generate_daily_smart_tips(form["cycle_day"], form["pregnancy_month"])

    return render_template(
        "tips.html",
        active_page="tips",
        tips_result=tips_result,
        form=form,
    )


@app.route("/fitness", methods=["GET", "POST"])
@login_required
def fitness():
    errors = []
    result = None
    form = {
        "age": "",
        "height_cm": "",
        "weight_kg": "",
        "goal": "maintenance",
        "activity_level": "low",
        "thyroid": "no",
        "pcos": "no",
        "pregnancy": "no",
    }

    if request.method == "POST":
        form["age"] = request.form.get("age", "").strip()
        form["height_cm"] = request.form.get("height_cm", "").strip()
        form["weight_kg"] = request.form.get("weight_kg", "").strip()
        form["goal"] = request.form.get("goal", "maintenance")
        form["activity_level"] = request.form.get("activity_level", "low")
        form["thyroid"] = "yes" if request.form.get("thyroid") == "yes" else "no"
        form["pcos"] = "yes" if request.form.get("pcos") == "yes" else "no"
        form["pregnancy"] = "yes" if request.form.get("pregnancy") == "yes" else "no"

        result, errors = generate_fitness_diet_plan(form)

    return render_template(
        "fitness.html",
        active_page="fitness",
        errors=errors,
        result=result,
        form=form,
    )


@app.route("/workout", methods=["GET", "POST"])
@login_required
def workout():
    form = {
        "age": "",
        "fitness_level": "beginner",
        "goal": "fitness",
        "activity_level": "low",
        "cycle_phase": "regular",
        "thyroid": "no",
        "pcos": "no",
        "pregnancy": "no",
    }
    result = None
    plan_id = None
    completed_keys = []
    streak_count = _calculate_workout_streak(current_user.id)
    errors = []

    if request.method == "POST":
        form, age, errors = _normalize_workout_input(request.form)

        if not errors:
            result = generate_daily_workout_plan(
                age,
                form["fitness_level"],
                form["goal"],
                form["activity_level"],
                form["cycle_phase"],
                form["thyroid"],
                form["pcos"],
                form["pregnancy"],
            )
            stored = _persist_workout_plan(current_user.id, form, age, result)
            plan_id = stored.id
    else:
        latest = WorkoutPlan.query.filter_by(user_id=current_user.id).order_by(WorkoutPlan.created_at.desc()).first()
        if latest:
            result = latest.plan_payload
            plan_id = latest.id
            form = {
                "age": str(latest.age),
                "fitness_level": latest.fitness_level,
                "goal": latest.goal,
                "activity_level": latest.activity_level,
                "cycle_phase": latest.cycle_phase,
                "thyroid": "yes" if latest.thyroid else "no",
                "pcos": "yes" if latest.pcos else "no",
                "pregnancy": "yes" if latest.pregnancy else "no",
            }

    if plan_id:
        completed_keys = _get_plan_completion_keys(current_user.id, plan_id)

    return render_template(
        "workout.html",
        active_page="workout",
        errors=errors,
        form=form,
        result=result,
        plan_id=plan_id,
        completed_keys=completed_keys,
        streak_count=streak_count,
    )


@app.route("/api/workout/plan", methods=["POST"])
@login_required
def workout_plan_api():
    payload = request.get_json(silent=True) or {}
    form, age, errors = _normalize_workout_input(payload)

    if errors:
        return jsonify({"errors": errors}), 400

    plan_payload = generate_daily_workout_plan(
        age,
        form["fitness_level"],
        form["goal"],
        form["activity_level"],
        form["cycle_phase"],
        form["thyroid"],
        form["pcos"],
        form["pregnancy"],
    )
    stored = _persist_workout_plan(current_user.id, form, age, plan_payload)

    return jsonify(
        {
            "plan_id": stored.id,
            "plan": plan_payload,
            "streak_count": _calculate_workout_streak(current_user.id),
        }
    )


@app.route("/api/workout/progress", methods=["POST"])
@login_required
def workout_progress_api():
    payload = request.get_json(silent=True) or {}
    plan_id = payload.get("plan_id")
    exercise_key = str(payload.get("exercise_key", "")).strip()

    if not plan_id or not exercise_key:
        return jsonify({"error": "plan_id and exercise_key are required."}), 400

    plan = WorkoutPlan.query.filter_by(id=plan_id, user_id=current_user.id).first()
    if not plan:
        return jsonify({"error": "Workout plan not found."}), 404

    existing = WorkoutCompletion.query.filter_by(
        user_id=current_user.id, plan_id=plan.id, exercise_key=exercise_key
    ).first()
    if not existing:
        db.session.add(
            WorkoutCompletion(user_id=current_user.id, plan_id=plan.id, exercise_key=exercise_key)
        )
        db.session.commit()

    completed_keys = _get_plan_completion_keys(current_user.id, plan.id)
    total = len(plan.plan_payload.get("all_exercises", []))

    return jsonify(
        {
            "completed_count": len(completed_keys),
            "total_count": total,
            "streak_count": _calculate_workout_streak(current_user.id),
            "completed_keys": completed_keys,
        }
    )


@app.route("/api/workout/history", methods=["GET"])
@login_required
def workout_history_api():
    plans = (
        WorkoutPlan.query.filter_by(user_id=current_user.id)
        .order_by(WorkoutPlan.created_at.desc())
        .limit(12)
        .all()
    )
    return jsonify({"plans": [plan.to_dict() for plan in plans]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
