# Flask Calculator for Docker and Kubernetes Practice

This is a simple Flask calculator app that you can:
- build as a Docker image
- push to Docker Hub
- pull and run anywhere
- deploy to Kubernetes

## Features

- Scientific keypad UI with DEG/RAD mode toggle
- Functions: sin, cos, tan, asin, acos, atan, sqrt, log, ln, factorial
- Constants and helpers: pi, e, Ans, inverse (1/x), powers, modulus
- Safe expression parsing on backend (no direct eval)
- Recent calculations history (last 12 items, session-based)
- Health endpoint: `/healthz`

## 1) Build the Docker image

```bash
docker build -t your-dockerhub-username/flask-calculator:1.0.0 .
```

## 2) Push image to Docker Hub

```bash
docker login
docker push your-dockerhub-username/flask-calculator:1.0.0
```

## 3) Pull and run for practice

```bash
docker pull your-dockerhub-username/flask-calculator:1.0.0
docker run -d -p 5000:5000 --name flask-calculator your-dockerhub-username/flask-calculator:1.0.0
```

Open in browser:
http://localhost:5000

Health check endpoint:
http://localhost:5000/healthz

## 4) Deploy to Kubernetes

Update image name in:
- `k8s/deployment.yaml`

Then apply:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods
kubectl get svc
kubectl describe pod -l app=flask-calculator
```

If using Minikube:

```bash
minikube service flask-calculator-service
```

If using Docker Desktop Kubernetes, access NodePort on localhost:
http://localhost:30050

Health check via NodePort:
http://localhost:30050/healthz

## 5) Clean up

```bash
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
docker rm -f flask-calculator
```
