# Diet Manager (Flask + Docker)

A simple Flask web app for tracking meals, calories, and macros. This project is made to practice Docker workflows.

## Features

- Add meal entries with calories, protein, carbs, and fats
- Mark meals as consumed
- Delete meals or clear all entries
- See aggregate nutrition totals
- SQLite-backed storage persisted in `/data`

## Run Locally (without Docker)

1. Create and activate a virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
flask --app app run --debug
```

4. Open `http://127.0.0.1:5000`

## Run with Docker

Build and run using Docker Compose:

```bash
docker compose up --build
```

Open `http://localhost:5000`

## Useful Docker commands

Stop containers:

```bash
docker compose down
```

Stop containers and remove volume data:

```bash
docker compose down -v
```

Rebuild after code changes:

```bash
docker compose up --build
```
