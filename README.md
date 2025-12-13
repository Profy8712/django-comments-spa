# 🌟 Django Comments SPA — Enterprise-Grade Documentation

A **production-ready Single Page Application (SPA)** for managing **hierarchical comments** with a strong focus on scalability, security, and modern backend architecture.

This project demonstrates a **Middle+/Senior-level Django backend solution**, suitable for real-world production use and technical interviews.

---

## 🚀 Key Capabilities

- Unlimited nested comments (tree structure)
- Image & text attachments
- Automatic image resizing (Pillow)
- Lightbox image viewer
- XSS protection with strict allowlist
- CAPTCHA spam protection
- Live preview before submission
- Pagination (25 root comments per page)
- Sorting by multiple fields
- Real-time WebSocket updates
- Full-text search with Elasticsearch
- Fully Dockerized infrastructure
- Ready for AWS EC2 deployment
- CI/CD automation with GitHub Actions

---

## 📁 Project Structure

```
django_comments_spa/
│── comments/
│   ├── models.py              # Comment & Attachment models
│   ├── serializers.py         # Nested serializers, validation, CAPTCHA
│   ├── views.py               # REST API + search API
│   ├── documents.py           # Elasticsearch documents
│   ├── consumers.py           # WebSocket consumers
│   ├── validators.py          # File validation rules
│   └── urls.py
│
│── core/
│   ├── settings.py            # Django, DRF, Channels, Celery, Elasticsearch
│   ├── routing.py             # WebSocket routing
│   ├── asgi.py
│   └── celery.py
│
│── frontend/                  # Vue 3 + Vite SPA
│   └── src/
│       ├── api/
│       ├── components/
│       ├── helpers/
│       └── App.vue
│
│── media/                     # Uploaded files
│── docker-compose.yml
│── Dockerfile.backend
│── Dockerfile.frontend
│── requirements.txt
│── manage.py
│── README.md
```

---

## 🧠 Backend Architecture

### Core Stack
- Python 3.12
- Django 4+
- Django REST Framework
- Django Channels (WebSockets)
- Celery (async tasks)
- RabbitMQ (message broker)
- Redis (Celery backend & Channels layer)
- PostgreSQL (main database)
- Elasticsearch 8 + Kibana (search & analytics)

### Key Design Decisions
- **Separation of concerns** (API, async tasks, search, real-time)
- **Event-driven updates** via WebSockets
- **Asynchronous processing** for heavy tasks
- **Search engine offloading** to Elasticsearch
- **Docker-first** development and deployment

---

## 🧵 Nested Comments

- Unlimited nesting using `parent` foreign key
- Recursive serialization
- Optimized queries with `select_related` and `prefetch_related`

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
- Fast indexing
- Independent search scaling
- Index rebuild support

---

## 🔐 Security

- Strict XSS protection (Bleach)
- Allowed tags only:
  - `<a>`
  - `<i>`
  - `<strong>`
  - `<code>`
- SQL injection protection via ORM
- CAPTCHA required for comment creation
- File type & size validation

---

## 📎 File Attachments

| Type | Rules |
|-----|------|
| Images | Auto-resized to max 320×240 |
| TXT files | ≤ 100 KB, UTF-8 only |

Upload endpoint:
```
POST /api/comments/<id>/upload/
```

---

## ⚡ Real-Time Updates

- Django Channels + Redis
- Broadcast on new comment creation
- All connected clients update instantly
- No page reload required

---

## 📦 Pagination & Sorting

Pagination:
- 25 root comments per page

Sorting:
- Username
- Email
- Created date (ASC / DESC)

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

Run:
```bash
docker compose up --build
```

Rebuild search index:
```bash
docker exec -it comments_backend python manage.py search_index --rebuild
```

---

## ☁️ AWS EC2 Deployment (Overview)

1. Launch Ubuntu 22.04 EC2 instance
2. Install Docker & Docker Compose
3. Clone repository
4. Configure `.env`
5. Run Docker Compose
6. Add Nginx reverse proxy
7. Enable HTTPS with Certbot
8. Configure GitHub Actions for CI/CD

---

## 🔄 CI/CD Pipeline

GitHub Actions workflow:
- SSH into EC2
- Pull latest code
- Rebuild containers
- Restart services

Supports zero-downtime deployment.

---

## 🧪 Testing

Test coverage includes:
- Nested comments logic
- File validators
- XSS sanitization
- Pagination behavior
- CAPTCHA validation
- WebSocket events
- Search indexing

Run tests:
```bash
python manage.py test
```

---

## 🎯 Project Purpose

This project showcases:
- Real-world Django architecture
- Async processing with Celery
- Message brokers & background workers
- Full-text search integration
- Production-ready Docker setup
- Cloud deployment readiness

---

## 👤 Author

**Alexander Kurin**  
Python Backend Developer

**Stack:**  
Django • FastAPI • Celery • Redis • RabbitMQ • Elasticsearch • Docker • PostgreSQL • AWS

---

## 📄 License
MIT
