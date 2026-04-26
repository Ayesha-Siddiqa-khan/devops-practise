# Boutique E-Commerce Microservices (CI/CD + Kubernetes)

A beginner-friendly, portfolio-grade DevOps project for a boutique shopping platform built with microservices, Docker, Kubernetes, and GitHub Actions.

## Architecture

Application flow:

User Browser -> Frontend (React + Nginx) -> API Gateway -> Internal Microservices -> PostgreSQL

Services:
- `frontend-service` (React + Nginx)
- `api-gateway` (single backend entrypoint)
- `auth-service` (register/login/JWT)
- `product-service` (boutique product catalog)
- `cart-service` (cart operations)
- `order-service` (place order + order history)
- `user-service` (profile + shipping address)
- `payment-service` (mock payment simulator)
- `postgres` (shared database)

Optional monitoring:
- Prometheus
- Grafana

## Project Structure

```text
boutique-ecommerce/
|-- frontend/
|-- api-gateway/
|-- auth-service/
|-- product-service/
|-- cart-service/
|-- order-service/
|-- user-service/
|-- payment-service/
|-- k8s/
|   |-- namespace.yaml
|   |-- deployments/
|   |-- services/
|   |-- configmaps/
|   |-- secrets/
|   |-- monitoring/
|-- .github/workflows/ci-cd.yml
|-- README.md
```

## Docker Images

Image naming in manifests:
- `yourdockerhubusername/frontend-service:latest`
- `yourdockerhubusername/api-gateway:latest`
- `yourdockerhubusername/auth-service:latest`
- `yourdockerhubusername/product-service:latest`
- `yourdockerhubusername/cart-service:latest`
- `yourdockerhubusername/order-service:latest`
- `yourdockerhubusername/user-service:latest`
- `yourdockerhubusername/payment-service:latest`

CI pipeline automatically pushes:
- `latest`
- commit SHA tag (`${{ github.sha }}`)

## Kubernetes Highlights

Each microservice deployment includes:
- 2 replicas
- Rolling updates
- `imagePullPolicy: Always`
- readiness probe
- liveness probe
- resource requests/limits

Kubernetes resources include:
- namespace: `boutique-app`
- ConfigMap: service URLs
- Secret: DB username/password, JWT secret, database URL
- Services: ClusterIP for internal services, NodePort for frontend

## GitHub Actions CI/CD

Workflow file: `.github/workflows/ci-cd.yml`

On push to `main` branch:
1. Checkout repository
2. Setup Docker Buildx
3. Login Docker Hub
4. Build all service images in parallel (matrix)
5. Push tags: `latest` and commit SHA
6. Configure kubeconfig from secret
7. Update Kubernetes image tags to SHA
8. Apply Kubernetes manifests
9. Wait for rollout status
10. Verify pods and services

Required GitHub Secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `KUBE_CONFIG`

## Run on Minikube

```bash
minikube start --driver=docker
kubectl apply -f k8s/
kubectl apply -f k8s/configmaps/
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/monitoring/
kubectl get pods -n boutique-app
kubectl get svc -n boutique-app
minikube service frontend-service -n boutique-app
```

## Monitoring Access (Optional)

- Prometheus service: `prometheus` (ClusterIP)
- Grafana NodePort: `30300`

Open Grafana in Minikube:

```bash
minikube service grafana -n boutique-app
```

Default Grafana credentials:
- Username: `admin`
- Password: `admin123`

## Beginner Notes

- Frontend only calls `/api/*` (never direct internal services).
- API Gateway routes requests to internal services.
- Business logic is intentionally simple so you can understand each service quickly.
- PostgreSQL tables are auto-created by services on startup.

## Next Improvements

- Add Redis for cart caching
- Add unit/integration tests per service
- Add Ingress + TLS
- Add autoscaling (HPA)
- Add centralized logs (Loki/ELK)
