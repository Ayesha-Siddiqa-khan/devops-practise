# FemCare AI - Women Health Dashboard System

Centralized Flask SaaS platform where health modules are database-driven.

## What this build does

- Dynamic main dashboard with search + category filters
- Module cards loaded from backend API (`/api/modules`), not hardcoded
- Shared module system for all users (same module catalog)
- Admin panel to create/edit/delete modules
- User authentication (register/login/logout)
- Dynamic module routes (`/module/<route>`)
- Health Overview Cards section (no charts)
- Existing women health tools retained (period, pregnancy, workout, thyroid, mental wellness, etc.)
- Diabetes and heart health companion with logs, alerts, insights timeline, and assistant

## Core architecture

- Backend: Flask + Flask-SQLAlchemy + Flask-Login
- Frontend: Jinja + Tailwind CDN + vanilla JavaScript
- Database: PostgreSQL (Docker) or SQLite fallback
- Dynamic module source of truth: `health_modules` table

## New Diabetes and Heart module

- UI page: `/diabetes-heart`
- Logs blood glucose, blood pressure, and heart rate
- Stores meal notes and medication entries
- Generates trend summaries and risk alerts
- Includes assistant Q&A endpoint for supportive guidance

### Diabetes and Heart API endpoints

- `POST /api/diabetes/log`
- `POST /api/heart/metrics`
- `POST /api/meal/log`
- `POST /api/medication/log`
- `GET /api/insights`
- `POST /api/assistant/query`

## PostgreSQL schema

See [schema_postgres.sql](schema_postgres.sql).

### `health_modules` table columns

- `id`
- `title`
- `description`
- `category`
- `route`
- `status`
- `icon`
- `target_url`
- `created_at`

## Folder structure

```text
period/
├── app.py
├── models/
│   ├── __init__.py
│   └── entities.py
├── services/
│   ├── period_service.py
│   ├── pregnancy_service.py
│   ├── risk_service.py
│   ├── leucorrhea_service.py
│   ├── women_health_service.py
│   ├── symptom_nlp_service.py
│   ├── labor_emergency_service.py
│   ├── breast_mental_service.py
│   ├── thyroid_service.py
│   ├── fitness_diet_service.py
│   ├── workout_service.py
│   ├── diabetes_heart_service.py
│   └── tips_service.py
├── routes/
│   ├── __init__.py
│   └── diabetes_heart.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── module_detail.html
│   ├── admin_modules.html
│   ├── admin_module_form.html
│   ├── auth_login.html
│   ├── auth_register.html
│   ├── period_tracker.html
│   ├── pregnancy_tracker.html
│   ├── health_checker.html
│   ├── fitness.html
│   ├── workout.html
│   ├── diabetes_heart.html
│   └── tips.html
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   ├── js/diabetes_heart.js
│   └── images/workouts/
├── schema_postgres.sql
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Run with Docker (recommended)

1. Build and start:

```bash
docker compose up --build
```

2. Open app:

- `http://localhost:5000`

3. Default admin account (seeded from env):

- Username: `admin`
- Password: `admin123`

4. Stop:

```bash
docker compose down
```

## Local run (without Docker)

1. Create venv and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Optional PostgreSQL DB URL (otherwise SQLite is used):

```bash
set DATABASE_URL=postgresql+psycopg://femcare:femcare@localhost:5432/femcare
```

3. Run app:

```bash
python app.py
```

4. Open:

- `http://localhost:5000`

## Admin module creator workflow

1. Login as admin
2. Go to `/admin/modules`
3. Add/edit/delete modules
4. Dashboard updates instantly for all users because cards are fetched from DB/API

## Safety disclaimer

This application is for educational and informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. In emergencies, consult a healthcare professional immediately.
