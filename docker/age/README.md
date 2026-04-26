# Flask Age Calculator (Docker Practice)

A simple Flask web app that calculates age from date of birth.

## Run Locally

```bash
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`

## Build Docker Image

```bash
docker build -t flask-age-calculator .
```

## Run Container

```bash
docker run -p 5000:5000 flask-age-calculator
```

Open `http://localhost:5000`
