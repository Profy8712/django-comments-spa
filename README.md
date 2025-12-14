# 🌟 Django Comments SPA — Enterprise-Grade Documentation

A **production-ready Single Page Application (SPA)** for managing **hierarchical comments**, designed with a strong focus on **backend architecture**, **security**, **scalability**, and **real-world production practices**.

This project demonstrates a **Middle+/Senior-level Django backend solution** with a modern SPA frontend, suitable for technical interviews and real production usage.

---

## 🎯 Project Goals (Assignment-Oriented Overview)

The goal of this project is to implement a **full-featured comments system** that clearly demonstrates:

- Backend-first architecture
- Secure and scalable API design
- Modern SPA interaction model
- Protection against spam and XSS
- Real-time data updates
- Production-ready deployment setup

Each requirement from the assignment is **explicitly covered and implemented**.

---

## 🚀 Key Capabilities

### 🧠 Backend (Core Focus)

- Unlimited nested comments (adjacency list model)
- RESTful API built with Django REST Framework
- Hybrid security model (JWT + CAPTCHA)
- Strong server-side XSS protection
- File upload handling with validation
- Image processing (automatic resizing via Pillow)
- Full-text search using Elasticsearch
- Real-time updates via WebSockets (Django Channels)
- Background processing with Celery
- Clean separation of concerns
- Optimized database queries
- Fully Dockerized services

### 🎨 Frontend (SPA Client)

- Vue 3 + Vite Single Page Application
- Comment tree rendering (nested replies)
- Live preview before submission
- CAPTCHA support for anonymous users
- JWT-based authorized actions
- Attachment upload UI
- Lightbox image viewer
- Real-time updates without page reload
- Clean separation between frontend and backend

---

## 🔐 Authentication & Security Flow (JWT + CAPTCHA)

This project implements a **hybrid security model**, widely used in production SPAs.

| User Type | Authentication | CAPTCHA |
|---------|---------------|--------|
| Anonymous | ❌ | ✅ |
| Authorized | JWT | ❌ |

### Why this approach?
- CAPTCHA protects against bots and spam
- JWT provides smooth UX for trusted users
- Stateless authentication (no sessions, no cookies)
- Scales well horizontally

---

## 🔑 JWT Authentication (Backend)

JWT is implemented using **Django REST Framework SimpleJWT**.

### Obtain Token
```
POST /api/auth/token/
```

```json
{
  "username": "alex2",
  "password": "Qwerty12345!"
}
```

Response:
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

Usage:
```
Authorization: Bearer <access_token>
```

---

## 📁 Project Structure

```
django_comments_spa/
│── comments/                  # Core comments logic
│   ├── models.py              # Comment & Attachment models
│   ├── serializers.py         # Validation, XSS, CAPTCHA logic
│   ├── views.py               # REST API views
│   ├── documents.py           # Elasticsearch documents
│   ├── consumers.py           # WebSocket consumers
│   ├── validators.py          # File validation rules
│   └── urls.py
│
│── accounts/                  # Authentication & JWT
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
│── core/                      # Project configuration
│   ├── settings.py            # Django, DRF, JWT, Channels, Celery
│   ├── routing.py             # WebSocket routing
│   ├── asgi.py
│   └── celery.py
│
│── frontend/                  # Vue 3 + Vite SPA
│── media/                     # Uploaded files
│── docker-compose.yml
│── Dockerfile.backend
│── Dockerfile.frontend
│── requirements.txt
│── manage.py
│── README.md
```

---

## 🧵 Nested Comments Implementation

- Adjacency list (`parent` ForeignKey)
- Unlimited nesting depth
- Recursive serialization
- Optimized with `select_related` and `prefetch_related`

This approach ensures good performance even with deep comment trees.

---

## 🔍 Full-Text Search (Elasticsearch)

Searchable fields:
- Comment text
- User name
- Email

Endpoint:
```
GET /api/search/comments/?q=alex
```

Features:
- Fuzzy matching (`AUTO`)
- Independent scaling
- Fast indexing

Rebuild index:
```bash
docker exec -it comments_backend python manage.py search_index --rebuild
```

---

## 🛡 XSS Protection & Validation

- Raw HTML is fully blocked
- Only allowed pseudo-tags:
  - [a]
  - [i]
  - [strong]
  - [code]
- Tags must be balanced and properly nested
- Validation is enforced server-side

---

## 📎 File Attachments

| Type | Rules |
|----|------|
| Images | JPG / PNG / GIF, auto-resized to 320×240 |
| Text | `.txt`, UTF-8, ≤ 100 KB |

Upload endpoint:
```
POST /api/comments/<id>/upload/
```

Uploads are allowed **only for authenticated users**.

---

## ⚡ Real-Time Updates

- Implemented with Django Channels + Redis
- WebSocket broadcast on new comment creation
- All connected clients update instantly
- No polling, no page reload

---

## 🐳 Dockerized Environment

Services:
- backend
- frontend
- postgres
- redis
- rabbitmq
- celery
- celery_beat
- elasticsearch
- kibana

Run locally:
```bash
docker compose up --build
```

---

## ☁️ Deployment Readiness (AWS EC2)

- Docker-based deployment
- Environment variables via `.env`
- Nginx reverse proxy
- HTTPS with Certbot
- CI/CD via GitHub Actions

---

## 🔄 CI/CD Pipeline

1. Push to GitHub
2. GitHub Actions triggered
3. SSH into EC2
4. Pull latest code
5. Rebuild containers
6. Restart services

Supports zero-downtime deployments.

---

## 🧪 Testing

Covered:
- Nested comments logic
- XSS validation
- CAPTCHA validation
- JWT permissions
- File validation
- Search indexing
- WebSocket events

Run tests:
```bash
python manage.py test
```

---

## 👤 Author

**Oleksandr Kurin**  
Python Backend Developer

**Stack:**  
Django • FastAPI • Celery • Redis • RabbitMQ • Elasticsearch • Docker • PostgreSQL • AWS

---

## 📄 License

MIT
