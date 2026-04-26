-- PostgreSQL schema for centralized dashboard modules and users

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS health_modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    description VARCHAR(280) NOT NULL,
    category VARCHAR(60) NOT NULL,
    route VARCHAR(150) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    icon VARCHAR(60) NOT NULL DEFAULT 'fa-heart',
    target_url VARCHAR(150),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_health_modules_category ON health_modules(category);
CREATE INDEX IF NOT EXISTS idx_health_modules_status ON health_modules(status);

CREATE TABLE IF NOT EXISTS workout_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    age INTEGER NOT NULL,
    fitness_level VARCHAR(30) NOT NULL,
    goal VARCHAR(40) NOT NULL,
    activity_level VARCHAR(20) NOT NULL,
    cycle_phase VARCHAR(20) NOT NULL DEFAULT 'regular',
    thyroid BOOLEAN NOT NULL DEFAULT FALSE,
    pcos BOOLEAN NOT NULL DEFAULT FALSE,
    pregnancy BOOLEAN NOT NULL DEFAULT FALSE,
    plan_payload JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workout_completions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES workout_plans(id) ON DELETE CASCADE,
    exercise_key VARCHAR(80) NOT NULL,
    completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_workout_completion UNIQUE (user_id, plan_id, exercise_key)
);

CREATE INDEX IF NOT EXISTS idx_workout_plans_user_id ON workout_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_workout_completions_user_plan ON workout_completions(user_id, plan_id);

CREATE TABLE IF NOT EXISTS health_metric_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    value_primary DOUBLE PRECISION,
    value_secondary DOUBLE PRECISION,
    unit VARCHAR(30),
    context VARCHAR(40),
    payload JSONB,
    logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medication_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    medicine_name VARCHAR(120) NOT NULL,
    dosage VARCHAR(120),
    schedule_time VARCHAR(20),
    reminder_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    notes VARCHAR(280),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meal_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    meal_type VARCHAR(40) NOT NULL,
    foods VARCHAR(400) NOT NULL,
    classification VARCHAR(20) NOT NULL,
    guidance VARCHAR(280),
    logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_health_metric_logs_user_type ON health_metric_logs(user_id, metric_type);
CREATE INDEX IF NOT EXISTS idx_health_metric_logs_time ON health_metric_logs(logged_at);
CREATE INDEX IF NOT EXISTS idx_meal_logs_user_time ON meal_logs(user_id, logged_at);
