from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class HealthModule(db.Model):
    __tablename__ = "health_modules"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(280), nullable=False)
    category = db.Column(db.String(60), nullable=False)
    route = db.Column(db.String(150), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default="active")
    icon = db.Column(db.String(60), nullable=False, default="fa-heart")
    target_url = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "route": self.route,
            "status": self.status,
            "icon": self.icon,
            "target_url": self.target_url,
            "created_at": self.created_at.isoformat(),
        }


class WorkoutPlan(db.Model):
    __tablename__ = "workout_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False)
    fitness_level = db.Column(db.String(30), nullable=False)
    goal = db.Column(db.String(40), nullable=False)
    activity_level = db.Column(db.String(20), nullable=False)
    cycle_phase = db.Column(db.String(20), nullable=False, default="regular")
    thyroid = db.Column(db.Boolean, nullable=False, default=False)
    pcos = db.Column(db.Boolean, nullable=False, default=False)
    pregnancy = db.Column(db.Boolean, nullable=False, default=False)
    plan_payload = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("workout_plans", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "fitness_level": self.fitness_level,
            "goal": self.goal,
            "activity_level": self.activity_level,
            "cycle_phase": self.cycle_phase,
            "thyroid": self.thyroid,
            "pcos": self.pcos,
            "pregnancy": self.pregnancy,
            "plan_payload": self.plan_payload,
            "created_at": self.created_at.isoformat(),
        }


class WorkoutCompletion(db.Model):
    __tablename__ = "workout_completions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("workout_plans.id"), nullable=False, index=True)
    exercise_key = db.Column(db.String(80), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("workout_completions", lazy=True))
    plan = db.relationship("WorkoutPlan", backref=db.backref("completion_logs", lazy=True))

    __table_args__ = (db.UniqueConstraint("user_id", "plan_id", "exercise_key", name="uq_workout_completion"),)


class HealthMetricLog(db.Model):
    __tablename__ = "health_metric_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    metric_type = db.Column(db.String(50), nullable=False, index=True)
    value_primary = db.Column(db.Float, nullable=True)
    value_secondary = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(30), nullable=True)
    context = db.Column(db.String(40), nullable=True)
    payload = db.Column(db.JSON, nullable=True)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = db.relationship("User", backref=db.backref("health_metric_logs", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "metric_type": self.metric_type,
            "value_primary": self.value_primary,
            "value_secondary": self.value_secondary,
            "unit": self.unit,
            "context": self.context,
            "payload": self.payload or {},
            "logged_at": self.logged_at.isoformat(),
        }


class MedicationLog(db.Model):
    __tablename__ = "medication_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    medicine_name = db.Column(db.String(120), nullable=False)
    dosage = db.Column(db.String(120), nullable=True)
    schedule_time = db.Column(db.String(20), nullable=True)
    reminder_enabled = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.String(280), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("medication_logs", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "medicine_name": self.medicine_name,
            "dosage": self.dosage,
            "schedule_time": self.schedule_time,
            "reminder_enabled": self.reminder_enabled,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }


class MealLog(db.Model):
    __tablename__ = "meal_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    meal_type = db.Column(db.String(40), nullable=False)
    foods = db.Column(db.String(400), nullable=False)
    classification = db.Column(db.String(20), nullable=False)
    guidance = db.Column(db.String(280), nullable=True)
    logged_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = db.relationship("User", backref=db.backref("meal_logs", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "meal_type": self.meal_type,
            "foods": self.foods,
            "classification": self.classification,
            "guidance": self.guidance,
            "logged_at": self.logged_at.isoformat(),
        }
