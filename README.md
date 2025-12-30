# 🌟 Django Comments SPA 
Production‑ready comments system with **nested threads**, **JWT authentication**, **CAPTCHA protection**, 
and **real‑time updates**.

The project demonstrates **backend‑first architecture** with a modern SPA frontend and realistic Docker‑based deployment.

## ⚡ TL;DR

- Full-stack production-style comments system
- Django + DRF + Channels + Celery + Redis
- Vue 3 SPA with real-time updates
- JWT auth + CAPTCHA hybrid security
- Dockerized, deployed on AWS EC2 with HTTPS

---

## 🎯 Project Purpose
This project was created as a **backend‑oriented test assignment / portfolio project**.

The goal is to demonstrate how a real‑world comments system can be:

- properly structured on the backend
- protected from spam and XSS
- extended with asynchronous workers
- updated in real time
- deployed to a real server using Docker

The focus is on **architecture, correctness, and deployment**, not just CRUD.

---

## 🧠 How the System Works (High‑Level Overview)

### User Flow

1. User opens SPA (Vue 3)
2. Frontend requests data from Django REST API
3. Anonymous users must solve CAPTCHA
4. Authorized users authenticate via JWT
5. Comment is validated server‑side (XSS, CAPTCHA, files)
6. Comment is saved to PostgreSQL
7. WebSocket event is broadcast to all clients
8. All connected clients update instantly

---

## 🏗 Architecture Overview

Browser (Vue SPA)
│
│ HTTPS / WSS
▼
Nginx (SSL, Proxy)
│
├── Django REST API
│ ├── JWT Auth
│ ├── CAPTCHA
│ └── Comments API
│
├── Django Channels (WebSockets)
│ └── Redis
│
└── Celery Workers
└── RabbitMQ

---

## 🚀 Core Capabilities

### Backend

- Django + Django REST Framework
- Unlimited nested comments (adjacency list)
- JWT authentication (SimpleJWT)
- CAPTCHA for anonymous users
- Server‑side XSS protection
- File uploads with validation
- Image resizing via Pillow
- WebSockets via Django Channels
- Redis for Channels and caching
- Celery for background tasks
- RabbitMQ as message broker
- Dockerized services

### Frontend

- Vue 3 + Vite
- Recursive comment tree
- Live preview before submit
- CAPTCHA UI
- JWT support
- Attachments & image lightbox
- WebSocket real‑time updates

---

## Authentication & Security

### Hybrid Security Model

| User type | JWT | CAPTCHA |
|---------|-----|---------|
| Anonymous | ❌ | ✅ |
| Authorized | ✅ | ❌ |

**Why this approach:**

- CAPTCHA protects from bots and spam
- JWT provides smooth UX for registered users
- Stateless authentication scales well

JWT tokens are stored in `localStorage` intentionally for SPA simplicity.
HttpOnly cookies can be used as an alternative in other setups.

---

## 🛡 Admin & Moderation Features

The system supports an **administrator role** with elevated permissions.

### Admin capabilities

- Delete any comment (including nested replies)
- Moderate user-generated content
- Bypass CAPTCHA
- Visible **ADMIN badge** in the UI

### Admin identification

Admin users are standard Django users with:

- `is_staff = true`
- `is_superuser = true`

Admin status is resolved via the `/api/accounts/me/` endpoint
and reflected in the frontend UI.

### Admin-only endpoint

| Endpoint | Method | Access |
|---|---|---|
| `/api/comments/admin/comments/<id>/` | DELETE | Admin only |

Unauthorized access returns **403 Forbidden**.

---

## 📁 Project Structure

django_comments_spa/
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # CI (tests/build) + CD (deploy to EC2)
│
├── accounts/                      # Auth domain (JWT, /me, user info)
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── comments/                      # Comments domain (tree, uploads, WS, tasks)
│   ├── migrations/
│   ├── admin.py
│   ├── consumers.py               # Django Channels (WebSocket)
│   ├── permissions.py             # Custom permissions (admin delete, etc.)
│   ├── routing.py                 # WS routes
│   ├── serializers.py
│   ├── tasks.py                   # Celery tasks (async processing)
│   ├── urls.py
│   └── views.py
│
├── core/                          # Project core (settings, ASGI/WSGI, Celery init)
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── asgi.py                    # ASGI app (API + WebSockets)
│   ├── wsgi.py                    # WSGI app (classic HTTP)
│   ├── celery.py                  # Celery app configuration
│   └── urls.py
│
├── frontend/                      # Vue 3 + Vite SPA
│   ├── public/
│   ├── src/
│   │   ├── api/                   # HTTP client wrappers (comments/accounts)
│   │   ├── components/            # UI components (AuthBar, CommentForm, Tree)
│   │   ├── helpers/
│   │   ├── i18n/                  # translations
│   │   ├── App.vue
│   │   └── main.js
│   ├── vite.config.js
│   └── package.json
│
├── nginx/
│   ├── Dockerfile
│   └── nginx.conf                 # reverse proxy + static/media + WS upgrade
│
├── media/                         # Uploaded files (runtime)
├── staticfiles/                   # Django collectstatic output (runtime)
│
├── docker-compose.yml             # Local dev stack
├── docker-compose.prod.yml        # Production stack (server)
├── Dockerfile.backend             # Backend image build
│
├── .env.local                     # Local environment variables
├── .env.prod                      # Production environment variables
├── env.example                    # Example env template
│
└── manage.py                      # Django entrypoint


---

## 🧵 Nested Comments

- `parent` ForeignKey (adjacency list)
- Unlimited depth
- Recursive serialization
- Optimized queries

---

## 🛡 XSS Protection

- HTML is blocked entirely
- Allowed pseudo‑tags:
  - `[a]`
  - `[i]`
  - `[strong]`
  - `[code]`
- Validation is enforced **server‑side only**

---

## 📎 File Upload Rules
Attachments are available for authorized users only (JWT)
This design prevents anonymous file uploads and reduces spam risk.

| Type | Rules |
|------|------|
| Images | JPG / PNG / GIF → resized to 320×240 |
| Text | `.txt`, UTF‑8, ≤ 100 KB |

---

## ⚡ Real‑Time Updates

- Django Channels + Redis
- WebSocket broadcast on new comment
- No polling, no page reload

---

## Internationalization (i18n)

The frontend UI is fully localized using **vue-i18n**.

Supported languages:
- English (EN)
- Russian (RU)
- Ukrainian (UK)
- German (DE)

All user-facing text is localized, including:
- Buttons and labels
- Tooltips and titles
- Confirmation dialogs
- Error and success messages
- Dynamic UI elements (e.g. reply toggles)

Language selection is persisted in `localStorage` and applied automatically on page reload.

---

## 🐳 Local Development (Docker)

### Requirements

- Docker  
- Docker Compose  

### Run Locally (default stack)

```bash
docker compose up -d --build
```
Local stack includes:

- backend  
- frontend  
- postgres  
- redis  
- rabbitmq  
- celery  
- celery_beat  

Frontend:  
http://localhost:5173  

Backend API:  
http://localhost:8000/api/  

Django admin:  
http://localhost:8000/admin/  

RabbitMQ UI:  
http://localhost:15672  
login: guest  
password: guest  

### Run Locally with Search (Elasticsearch + Kibana)

Search services are optional and started via Docker Compose profile `search`.

```bash
docker compose --profile search up -d --build
```

Local stack additionally includes:

- elasticsearch  
- kibana  

Elasticsearch:  
http://localhost:9200  

Kibana:  
http://localhost:5601  

### Notes

- Elasticsearch and Kibana are not started by default
- Search functionality is disabled unless the `search` profile is enabled
- This setup reduces resource usage and speeds up local development
- Recommended for CI and low-resource environments

---

## ☁️ AWS EC2 Deployment (Production-Style)

### Environment

- AWS EC2 (Ubuntu)
- Docker + Docker Compose
- Nginx as reverse proxy
- HTTPS (Let’s Encrypt)
- Public domain name (DuckDNS)

### Deployment Overview

The application is deployed on a **public AWS EC2 instance** using a
**production-style setup**:

- Dockerized backend and services
- Nginx handles HTTPS termination
- Frontend (SPA) is served as static files
- Backend API is proxied through Nginx
- WebSocket connections are supported over **WSS**

---

## 🌐 Public Access

The application is available via a public domain name.

### Frontend (SPA)

```text
https://comments-spa-t.duckdns.org/
```

### Backend API

```text
https://comments-spa-t.duckdns.org/api/
```

### Comments API

Public endpoint for listing and creating comments.

```text
https://comments-spa-t.duckdns.org/api/comments/
```

- `GET` — list comments (public)
- `POST` — create comment  
  - anonymous users → **CAPTCHA required**
  - authenticated users → **JWT**, no CAPTCHA

### CAPTCHA Endpoint

```text
https://comments-spa-t.duckdns.org/captcha/
```

### WebSocket Endpoint

```text
wss://comments-spa-t.duckdns.org/ws/comments/
```
### JWT Authentication Endpoint

Used to obtain **access** and **refresh** tokens.

```yaml
POST https://comments-spa-t.duckdns.org/api/auth/token/
```

**Request body (JSON):**
```json
{
  "username": "<username>",
  "password": "<password>"
}
```

**Response:**
```json
{
  "access": "<JWT access token>",
  "refresh": "<JWT refresh token>"
}
```
### 🧰 JWT via API (optional)

JWT tokens can also be obtained directly via API for debugging purposes:

POST /api/auth/token/

This is **not required** for normal usage — the UI login is the recommended way.

---

## 🧩 Configuration Strategy

- Separate `.env` files are used for local and production environments
- Docker Compose configuration differs between development and deployment
- Environment separation avoids hard-coded values and accidental leaks
- Production configuration is deployment-specific

---

## 🧪 Test Credentials

The application is deployed for **testing and review purposes**.

You can use the following credentials to test:
- JWT authentication
- authorized comment posting
- file uploads
- WebSocket updates

**Test user**
- Login: `user`
- Password: `User12345!`

⚠️ These credentials are provided **for testing only**  
and have no administrative privileges.

---

## 🚀 CI/CD (GitHub Actions)
This project uses **GitHub Actions** to run CI checks and automatically deploy to **AWS EC2**.

### ✅ CI (Continuous Integration)

CI runs on every **push** and **pull request** to `main` and includes:

- Backend checks:
  - `python manage.py check`
- Frontend build:
  - `npm run build`

### 🚚 CD (Continuous Deployment)

CD runs on **push to `main`** (after CI succeeds) and performs the following steps:

- connects to the AWS EC2 instance via **SSH**
- pulls the latest `main` branch
- rebuilds and restarts Docker containers
- runs database migrations
- collects static files
- verifies deployment via healthcheck

Deployment is executed by:

```text
/home/ubuntu/django-comments-spa/deploy.sh
```
📄 Workflow file
.github/workflows/ci-cd.yml

🔐 Required GitHub Secrets

Add these secrets in:
GitHub Repo → Settings → Secrets and variables → Actions

EC2_HOST         # Public IP or domain of EC2
EC2_USER         # Usually: ubuntu
EC2_SSH_KEY      # Private SSH key for deployment (ed25519)
EC2_PROJECT_DIR  # /home/ubuntu/django-comments-spa

✅ Healthcheck URLs

CD verifies that the application is live using:

https://comments-spa-t.duckdns.org/
https://comments-spa-t.duckdns.org/api/comments/captcha/

You can check pipeline runs in:
GitHub → Actions

---

## 📊 Database Schema

The database schema is provided in:

docs/db_schema.sql

yaml
Copy code

The file can be opened in **MySQL Workbench** to review:
- table structure
- relationships
- constraints

> Note: The project uses **PostgreSQL**, but MySQL Workbench is used
> as a universal schema viewer for review purposes.

---

## 🧾 OpenAPI Schema & Swagger Documentation

The project exposes a **machine-readable OpenAPI schema** and an
**interactive Swagger UI** describing all API endpoints, serializers,
request/response structures, authentication methods, and error formats.

This documentation can be used for:

- API client generation
- integration with external systems
- automated testing
- API validation and versioning
- interactive API exploration and debugging

### 🔗 Documentation Endpoints

#### Swagger UI (Interactive)

**Production:**

```text
https://comments-spa-t.duckdns.org/api/docs/
https://comments-spa-t.duckdns.org/api/schema/
```
---
## 👤 Author

**Oleksandr Kurin**  
Python Backend Developer

**Tech stack:**
- Django
- Django REST Framework
- Celery
- Redis
- RabbitMQ
- PostgreSQL
- Docker
- Nginx
- AWS
- WebSockets
- Vue 3

---

## 📄 License

MIT