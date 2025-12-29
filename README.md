# 🌟 Django Comments SPA — Production‑Style Backend Project

## ⚡ TL;DR

- Full-stack production-style comments system
- Django + DRF + Channels + Celery + Redis
- Vue 3 SPA with real-time updates
- JWT auth + CAPTCHA hybrid security
- Dockerized, deployed on AWS EC2 with HTTPS

A **production‑style Single Page Application (SPA)** for managing **hierarchical comments**, built with a strong focus on **backend architecture**, **security**, **scalability**, and **real‑world deployment practices**.

This project demonstrates  Django backend solution** combined with a modern SPA frontend and a realistic Docker‑based deployment on AWS EC2.

---

## 🎯 Project Purpose

The goal of this project is to demonstrate how a **real‑world comments system** can be:

- Architected backend‑first
- Protected from spam and XSS
- Scaled with async workers and message brokers
- Updated in real‑time via WebSockets
- Deployed to a real server environment

The project intentionally goes beyond simple CRUD to show **production thinking**.

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

## 🔐 Authentication & Security
## 🔁 Hybrid Security Model
| User Type | Authentication | CAPTCHA |
|----------|----------------|---------|
| Anonymous | ❌ | ✅ |
| Authorized | JWT | ❌ |

Why:

- CAPTCHA protects from bots
- JWT gives smooth UX
- Stateless & scalable

---
## 🧠 JWT Authentication Concept

This project uses **JWT (JSON Web Tokens)** to authenticate users
and protect sensitive API endpoints.

JWT is implemented using **Django REST Framework SimpleJWT** and is
designed for a **SPA + API architecture**.

### Why JWT?

- Stateless authentication
- No server-side sessions
- Scales well for distributed systems
- Ideal for Vue SPA + Django REST API

---

## 🔑 Authentication Endpoints

### Obtain JWT Tokens

```http
POST /api/auth/token/
```
Request:

{
  "username": "user",
  "password": "User12345!"
}


Response:

{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}


access — used for authenticated API requests

refresh — used to renew access token

Refresh Access Token
POST /api/auth/token/refresh/


Request:

{
  "refresh": "<refresh_token>"
}


Response:

{
  "access": "<new_access_token>"
}

🧪 How JWT Is Used in This Project
✅ Primary method (UI)

JWT authentication is handled via the Login form in the frontend UI:
User enters username and password
Backend returns JWT tokens
Tokens are stored in localStorage
Frontend automatically attaches:
Authorization: Bearer <access_token>
to protected API requests.

No manual token handling is required.
---
## 🔍 How to Verify JWT Usage

### Browser (DevTools)

1. Open **DevTools → Network**
2. Create a comment as an authenticated user
3. Open request:  
   `POST /api/comments/`
4. Verify request headers:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```
This confirms that:

JWT access token is attached automatically

protected endpoints are accessed correctly

frontend ↔ backend authentication works as expected

🛡 Protected Endpoints Overview
Endpoint	Access
GET /api/comments/	Public
POST /api/comments/	Anonymous + CAPTCHA or JWT
POST /api/comments/<id>/upload/	JWT only
DELETE /api/comments/<id>/	Admin only
GET /api/search/comments/	Public

---
## 🛡 Admin & Moderation Features

The system includes a dedicated **administrator role** with elevated permissions.

### Admin capabilities

- Delete any comment (including nested replies)
- Moderate user-generated content
- Perform actions without CAPTCHA
- Visible **ADMIN badge** in the UI

### Admin authentication

Admin users are standard Django users with:

- `is_staff = true`
- `is_superuser = true`

Admin status is determined via the `/api/accounts/me/` endpoint
and reflected in the frontend UI.

### Admin-only endpoint

| Endpoint | Method | Access |
|-------|--------|-------|
| `/api/comments/admin/comments/<id>/` | DELETE | Admin only |

Unauthorized access returns **403 Forbidden**.


## 🧩 JWT Configuration (settings.py)

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
```

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```



## 📁 Project Structure

```
## 📁 Project Structure

```text
django_comments_spa/
├── accounts/                 # Authentication, JWT, /me endpoint
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
│
├── comments/                 # Comments domain logic
│   ├── models.py             # Comment & Attachment models
│   ├── serializers.py
│   ├── views.py              # Public & admin APIs
│   ├── permissions.py        # Admin permissions
│   ├── urls.py
│   └── validators.py
│
├── core/
│   ├── settings/
│   │   ├── base.py           # Shared settings
│   │   ├── local.py          # Local development
│   │   └── production.py     # AWS production
│   │
│   ├── asgi.py               # ASGI (Channels)
│   ├── wsgi.py
│   ├── celery.py
│   └── urls.py
│
├── frontend/                 # Vue 3 SPA
│   ├── src/
│   │   ├── api/              # API clients
│   │   ├── components/
│   │   ├── helpers/
│   │   ├── App.vue
│   │   └── main.js
│   ├── dist/                 # Production build
│   └── Dockerfile
│
├── nginx/                    # Docker Nginx config
│   ├── Dockerfile
│   └── nginx.conf
│
├── media/                    # Uploaded files
├── staticfiles/              # Collected static files
│
├── docker-compose.yml        # Local stack
├── docker-compose.prod.yml   # Production stack
├── Dockerfile.backend
│
├── manage.py
├── requirements.txt
├── README.md
├── .env.local
└── .env.prod

```

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

### Run Locally

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
- elasticsearch
- kibana

Frontend:  
http://localhost:5173

Backend API:  
http://localhost:8000/api/

Django admin:
http://localhost:8000/admin/

RabbitMQ UI:
http://localhost:15672
login guest, password guest

Elasticsearch:
http://localhost:9200

Kibana:
http://localhost:5601
---

## ☁️ AWS EC2 Deployment (Production-Style)

### Environment

- AWS EC2 (Ubuntu)
- Docker + Docker Compose
- Nginx as reverse proxy
- HTTPS (Let’s Encrypt)
- Public domain name (DuckDNS)

---

### Deployment Overview

The application is deployed on a **public AWS EC2 instance** using a
**production-style setup**:

- Dockerized backend and services
- Nginx handles HTTPS termination
- Frontend (SPA) is served as static files
- Backend API is proxied through Nginx
- WebSocket connections are supported over **WSS**

This setup reflects a **realistic production environment** suitable for:
- backend test assignments
- portfolio projects
- internal tools
- small to medium workloads

---

## 🌐 Public Access

The application is available via a public domain name.

---

### Frontend (SPA)

```text
https://comments-spa-t.duckdns.org/
```

---

### Backend API

```text
https://comments-spa-t.duckdns.org/api/
```

---

### Comments API

Public endpoint for listing and creating comments.

```text
https://comments-spa-t.duckdns.org/api/comments/
```

- `GET` — list comments (public)
- `POST` — create comment  
  - anonymous users → **CAPTCHA required**
  - authenticated users → **JWT**, no CAPTCHA

---

### CAPTCHA Endpoint

```text
https://comments-spa-t.duckdns.org/captcha/
```

---

### WebSocket Endpoint

```text
wss://comments-spa-t.duckdns.org/ws/comments/
```

---

### JWT Authentication Endpoint

Used to obtain **access** and **refresh** tokens.

```yaml
POST https://comments-spa-t.duckdns.org/api/auth/token/
```

**Request body (JSON):**
```json
{
  "username": "user",
  "password": "User12345!"
}
```

**Response:**
```json
{
  "access": "<JWT access token>",
  "refresh": "<JWT refresh token>"
}
```


---

## 🔐 HTTPS Details

- HTTPS is enabled via **Let’s Encrypt**
- Nginx terminates SSL and proxies traffic to Docker containers
- WebSocket connections are upgraded correctly (`wss://`)
- No insecure mixed-content requests are used

This ensures:
- encrypted traffic
- browser-trusted SSL certificate
- correct SPA + API + WebSocket integration

---

## 🧩 Configuration Strategy

- `.env` files differ between **local** and **server** environments
- `docker-compose.yml` is adapted for deployment needs
- This separation is **intentional and correct**
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
## 🔐 JWT Authentication

The project uses **JWT (access + refresh)** authentication.

- Tokens are stored in `localStorage`
- UI updates automatically via `auth-changed` event
- Admin users are marked with **ADMIN badge**

Authorized mode enables:
- posting comments without CAPTCHA
- file uploads
- admin actions (delete comments)
- real-time WebSocket updates

---

## 🧪 Test Credentials

**User (non-admin)**  
- Login: `user`  
- Password: `User12345!`

⚠️ For testing only.  
This user has **no admin permissions**.

---

## 🔑 Login (UI – recommended)

1. Open the application:
```text
https://comments-spa-t.duckdns.org/
```
In the Auth panel:
enter username
enter password
click Login

After successful login:
status changes to Authorized
JWT tokens are saved to localStorage
file uploads become available
CAPTCHA is disabled

if user is staff/superuser → ADMIN badge appears

🚪 Logout

To return to anonymous mode, click Logout in the UI.

Or manually via browser console:

localStorage.removeItem("access");
localStorage.removeItem("refresh");
location.reload();


After logout:

application works in anonymous mode
CAPTCHA is required again
admin actions are disabled

🧰 Get JWT Tokens via API (optional / debugging)

You can also obtain tokens directly via API:

POST https://comments-spa-t.duckdns.org/api/auth/token/

{
  "username": "user",
  "password": "User12345!"
}


Response:

{
  "access": "<JWT access token>",
  "refresh": "<JWT refresh token>"
}


Store tokens manually (DevTools → Console):

fetch("https://comments-spa-t.duckdns.org/api/auth/token/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "user",
    password: "User12345!"
  }),
})
  .then(r => r.json())
  .then(t => {
    localStorage.setItem("access", t.access);
    localStorage.setItem("refresh", t.refresh);
    window.dispatchEvent(new Event("auth-changed"));
    location.reload();
  });

---
## 🚀 CI/CD (GitHub Actions)

This project uses **GitHub Actions** to run CI checks and automatically deploy to **AWS EC2**.

---

### ✅ CI (Continuous Integration)

CI runs on every **push** and **pull request** to `main` and includes:

- Backend checks:
  - `python manage.py check`
- Frontend build:
  - `npm run build`

---

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
## 📊 Elasticsearch & Kibana

The project integrates Elasticsearch for full-text search
and Kibana for analytics and monitoring.

Implemented features:
- Comments indexing
- Real-time analytics dashboards
- Activity monitoring (comments per day/hour)
- User behavior analysis
- Attachment statistics

Kibana dashboards demonstrate system observability
and scalability readiness.

### 🔗 Access URLs

**Production (if enabled):**

- Kibana:  
  `https://comments-spa-t.duckdns.org/kibana/`  
  *(or via SSH tunnel / internal access, depending on deployment)*

- Elasticsearch (internal service):  
  `http://elasticsearch:9200`

**Local environment:**

- Kibana:  
  `http://localhost:5601`

- Elasticsearch:  
  `http://localhost:9200`

This integration shows how the application can evolve
from a simple CRUD system into a **search- and analytics-driven platform**.

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

---

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