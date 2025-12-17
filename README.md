# 🌟 Django Comments SPA — Production‑Style Backend Project

A **production‑style Single Page Application (SPA)** for managing **hierarchical comments**, built with a strong focus on **backend architecture**, **security**, **scalability**, and **real‑world deployment practices**.

This project demonstrates a **Middle+/Senior‑level Django backend solution** combined with a modern SPA frontend and a realistic Docker‑based deployment on AWS EC2.

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
## 🧠 JWT Concept in This Project

The project uses **JWT (JSON Web Tokens)** to authenticate users and protect sensitive API endpoints.

### Why JWT?

- Stateless authentication
- No server-side sessions
- Scales well in distributed systems
- Ideal for SPA + API architecture

We use **Django REST Framework SimpleJWT**.

---

## 🔑 Authentication Endpoints

### Obtain JWT Token

`POST /api/auth/token/`

Request:

```json
{
  "username": "alex2",
  "password": "Qwerty12345!"
}
```

Response:

```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

- `access` → used for API requests
- `refresh` → used to renew access token

---

### Refresh Access Token

`POST /api/auth/token/refresh/`

Request:

```json
{
  "refresh": "<refresh_token>"
}
```

Response:

```json
{
  "access": "<new_access_token>"
}
```

---

## 🧪 How to Use JWT (API)

### Authorized Request Example

```bash
curl -X POST http://localhost:8000/api/comments/   -H "Authorization: Bearer ACCESS_TOKEN_HERE"   -H "Content-Type: application/json"   -d '{
    "user_name": "jwt_user",
    "email": "jwt@test.com",
    "text": "Comment created with JWT"
  }'
```

Result:

- ✅ Comment is created
- ❌ CAPTCHA is NOT required

---

### Unauthorized Request (Anonymous)

```bash
curl -X POST http://localhost:8000/api/comments/   -H "Content-Type: application/json"   -d '{
    "user_name": "anon",
    "email": "anon@test.com",
    "text": "Anonymous comment"
  }'
```

Result:

- ❌ 400 Bad Request
- ❌ CAPTCHA required

---

## 🌐 How to Use JWT in Browser

### Step 1: Get Token (DevTools → Console)

```js
fetch("http://localhost:8000/api/auth/token/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "alex2",
    password: "Qwerty12345!"
  })
})
.then(r => r.json())
.then(t => localStorage.setItem("access", t.access))
```

---

### Step 2: Send Authorized Request

```js
fetch("http://localhost:8000/api/comments/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + localStorage.getItem("access")
  },
  body: JSON.stringify({
    user_name: "jwt_user",
    email: "jwt@test.com",
    text: "JWT comment from browser"
  })
})
.then(r => r.json())
.then(console.log)
```

Result:

- ✅ Comment created
- ❌ CAPTCHA hidden / not required

---

## 🔍 How to Verify JWT Is Used

### Network Tab (Browser)

1. Open DevTools → Network
2. Submit a comment
3. Click `/api/comments/`
4. Check headers:

`Authorization: Bearer eyJhbGciOiJIUzI1NiIs...`

---

## 🛡 Protected Endpoints

| Endpoint | Access |
|-------|-------|
| `GET /api/comments/` | Public |
| `POST /api/comments/` | Anonymous + CAPTCHA OR JWT |
| `POST /api/comments/<id>/upload/` | JWT only |
| `GET /api/search/comments/` | Public |

---

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
django_comments_spa/
├── accounts/            # Authentication & JWT
├── comments/            # Comments logic, serializers, validators
├── core/
│   ├── settings/        # Environment-based Django settings
│   │   ├── __init__.py
│   │   ├── base.py      # Base settings (shared)
│   │   ├── local.py     # Local / development settings
│   │   └── production.py# Production settings
│   ├── __init__.py
│   ├── asgi.py          # ASGI entrypoint (Django Channels)
│   ├── celery.py        # Celery app
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI entrypoint
├── frontend/            # Vue 3 SPA
├── media/               # Uploaded files
├── staticfiles/         # Collected static files (production)
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile.backend
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

## 🐳 Local Development (Docker)

### Requirements

- Docker
- Docker Compose

### Run Locally

```bash
docker compose up --build
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

## ☁️ AWS EC2 Deployment (Production‑Style)

### Environment

- Ubuntu EC2 instance
- Docker + Docker Compose
- Nginx as reverse proxy
- HTTPS with **self‑signed SSL certificate**
- No domain name

### Why Self‑Signed?

- Deployment via IP address
- Resource‑limited environment
- Focus on backend architecture, not PKI

### Production Stack Differences

| Feature | Local | AWS |
|------|------|-----|
| Elasticsearch | ✅ | ❌ |
| Kibana | ✅ | ❌ |
| Nginx | ❌ | ✅ |
| HTTPS | ❌ | ✅ (self‑signed) |

### Production Startup

```bash
docker compose up -d --build
sudo systemctl reload nginx
```

---

## 🧩 Configuration Strategy

- `.env` differs between local and server
- `docker-compose.yml` adapted on server
- This is **intentional and correct**
- Server configs are deployment‑specific
---

## 🌐 How to Access the Application (AWS EC2)

The application is deployed on an **AWS EC2 instance** and is доступна **по IP‑адресу сервера**.

### Public Access

Replace `SERVER_IP` with the actual public IPv4 address of the EC2 instance.

**Frontend (SPA):**
```
https://SERVER_IP/
```

> ⚠️ HTTPS uses a **self‑signed SSL certificate**, so the browser will show a security warning.
> This is expected and acceptable for demonstration and backend‑focused projects.

**Backend API:**
```
https://SERVER_IP/api/
```

**CAPTCHA endpoint:**
```
https://SERVER_IP/api/captcha/
```

**WebSocket endpoint:**
```
wss://SERVER_IP/ws/comments/
```

⚠️ **Important:**  
HTTPS is enabled using a **self-signed SSL certificate**.  
The browser security warning is expected and acceptable for this project.

---

## 🧪 Test Credentials

The application is deployed for **testing and review purposes**.

You can use the following credentials to test **authenticated functionality**:
JWT authentication, authorized comment posting, and file uploads.

**Test user**
- Login: `user`
- Password: `User12345!`

⚠️ These credentials are provided **for testing only** and have no administrative privileges.

---

## 🔐 HTTPS Details (Important)

- HTTPS is enabled via a **self-signed SSL certificate**
- No domain name is used (IP-based access)
- Nginx terminates SSL and proxies traffic to Docker containers
- This setup reflects a **realistic production-style deployment** for:
  - test assignments
  - internal tools
  - backend portfolio projects
  - resource-limited environments

---
## 📊 Database Schema

The database schema is provided in `docs/db_schema.sql`.

The file can be opened in **MySQL Workbench** to review:
- table structure
- relationships
- constraints

Note: The project uses PostgreSQL, but MySQL Workbench is used
as a universal schema viewer for review purposes.

## 👤 Author

**Oleksandr Kurin**  
Python Backend Developer

Stack: Django • DRF • Celery • Redis • RabbitMQ • Docker • PostgreSQL • AWS • Vue 3

---

## 📄 License

MIT

---

