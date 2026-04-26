# Zeenkaar Flask E-Commerce Web App

Full-featured Flask e-commerce web application with:
- User registration and login
- Product search and category dropdown filtering
- Shopping cart
- Secure card payment via Stripe Checkout
- Order creation and order history
- PostgreSQL database with SQLAlchemy ORM
- Dockerized deployment for consistent environment setup

## 1) Project Structure

zeenkaar/
  app/
    __init__.py
    config.py
    extensions.py
    models/
    routes/
    services/
    templates/
    static/
  migrations/
  .env.example
  docker-compose.yml
  Dockerfile
  requirements.txt
  run.py
  seed.py

## 2) Prerequisites

- Docker Desktop installed
- Stripe account (test mode keys)

## 3) Environment Setup

1. Create .env from template:
   copy .env.example .env

2. Open .env and set values:
   - SECRET_KEY
   - STRIPE_SECRET_KEY
   - STRIPE_PUBLISHABLE_KEY

## 4) Build and Start

Run:
  docker-compose up --build

This starts:
- Web app on http://localhost:5000
- PostgreSQL on localhost:5432

## 5) Database Migration

Run in a new terminal:
  docker-compose exec app flask db init
  docker-compose exec app flask db migrate -m "initial schema"
  docker-compose exec app flask db upgrade

If init already ran once, skip it next time.

## 6) Seed Sample Data

Run:
  docker-compose exec app python seed.py

## 7) How Checkout Works Securely

- App creates a Stripe Checkout Session on the server side.
- User enters card details on Stripe-hosted page.
- On success, Stripe returns session id.
- App verifies payment status using Stripe API.
- Only after verified paid status does app create the order.

Use Stripe test cards in test mode.

## 8) Core User Flow

1. Register account
2. Login
3. Browse products
4. Search by name/description
5. Filter by category dropdown
6. Add items to cart
7. Checkout securely with Stripe
8. View orders

## 9) Deployment Guide for Any Environment

### Option A: Docker Compose on VM/Server

1. Install Docker and Compose plugin
2. Clone project to server
3. Create .env with production secrets
4. Run:
   docker-compose up --build -d
5. Run migrations:
   docker-compose exec app flask db migrate -m "prod migration"
   docker-compose exec app flask db upgrade
6. Seed data only if needed:
   docker-compose exec app python seed.py
7. Put Nginx or cloud load balancer in front of port 5000
8. Enable HTTPS (Lets Encrypt or cloud SSL)

### Option B: Container Platform (ECS, Azure Container Apps, Render)

1. Build image from Dockerfile
2. Push image to container registry
3. Provision managed PostgreSQL
4. Set env vars from .env values
5. Run migration job before traffic cutover
6. Expose container port 5000
7. Configure HTTPS and custom domain

## 10) Important Production Notes

- Keep Stripe keys and app secrets in secret manager, not in code.
- Run with HTTPS in production.
- Rotate secrets periodically.
- Add Stripe webhook endpoint for async payment events if needed.
