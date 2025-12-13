
# 🌟 Django Comments SPA — Full Professional Documentation

A production-ready Single Page Application (SPA) for managing **hierarchical comments**, complete with:
✔ Unlimited nested replies  
✔ Image & text attachments  
✔ Image auto‑resize  
✔ Lightbox viewer  
✔ XSS filtering + allowed safe HTML  
✔ CAPTCHA verification  
✔ Preview before submit  
✔ Pagination (25 per page)  
✔ Sorting by multiple fields  
✔ WebSocket real‑time updates  
✔ Dockerized full-stack environment  
✔ AWS EC2 deployment guide  
✔ CI/CD automation (GitHub Actions)  

This README is a **full, comprehensive, enterprise‑grade version** suitable for GitHub, portfolio, and production teams.

---

# 📁 Project Structure (Repository Layout)

```
django_comments_spa/
│── comments/                 # Django app: comments logic, attachments, validation, sanitizing
│     ├── models.py           # Comment + Attachment models
│     ├── serializers.py      # API serializers with nested children
│     ├── views.py            # List/Create API, attachment upload
│     ├── consumers.py        # WebSocket consumer for live updates
│     ├── utils/
│     │     └── sanitize.py   # HTML sanitizing rules
│     ├── validators.py       # File size/type validators
│     └── urls.py
│
│── core/                      # Django project configuration
│     ├── settings.py          # DRF, Channels, CORS, XSS, pagination
│     ├── routing.py           # WebSocket routing
│     └── asgi.py
│
│── frontend/                  # Vue 3 + Vite SPA
│     ├── public/
│     └── src/
│          ├── api/            # API clients
│          ├── components/     # All Vue components
│          ├── helpers/        # Sanitizer, preview parser
│          └── App.vue         # Main SPA
│
│── media/                     # Uploaded attachments
│── docker-compose.yml
│── Dockerfile.backend
│── Dockerfile.frontend
│── requirements.txt
│── manage.py
│── README.md (this file)
```

---

# 🎯 Core Features — Explained in Detail

## 1️⃣ Nested Comments (Unlimited Depth)

- Each comment can have **any number of replies**.
- Replies are displayed as an expanding **tree structure**.
- Backend returns nested structure via recursive serializer:
```
children: [ ... ]
```

## 2️⃣ Sorting (Root Comments Only)

Sort options on frontend:

- Username A→Z / Z→A  
- Email A→Z / Z→A  
- Created date (oldest first)  
- Created date (newest first — **default LIFO**)  

Backend supports ordering via:
```
/api/comments/?ordering=-created_at
```

## 3️⃣ Pagination — 25 Comments Per Page

Django REST Framework config:
```
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
}
```
Frontend displays:
- Page number  
- Next/Prev buttons  
- Keeps page state even after new comment appears  

## 4️⃣ File Attachments

### Allowed types:
| Type | Limit | Notes |
|------|--------|-------|
| JPG / PNG / GIF | Auto resized to **max 320×240** | Uses Pillow |
| TXT | ≤ 100 KB | UTF‑8 only |

Uploader:
```
POST /api/comments/<comment_id>/upload/
```

## 5️⃣ Image Lightbox Viewer
- Clicking an image opens it in full preview  
- Supports mobile gestures  
- Disabled for TXT files  

## 6️⃣ HTML Safe Tags (Pseudo-Markup)

User is allowed to input ONLY:
```
<a href="" title=""></a>
<i></i>
<strong></strong>
<code></code>
```

Sanitized using **bleach**:
- Removes unsafe attributes  
- Rejects JavaScript in links  
- Ensures valid XHTML closure  

## 7️⃣ Preview Before Submit
- User can see comment rendering before sending  
- Sanitized preview (safe HTML only)  

## 8️⃣ CAPTCHA (Spam Protection)
Uses `django-simple-captcha`:
- Key + value pair required for comment creation  
- Throttles bots  

## 9️⃣ Real-Time Updates (WebSockets)
Powered by **Django Channels + Redis**:
- When a comment is created, backend sends:
```
{ "type": "comment_created" }
```
- All connected clients auto-refresh the current page  

---

# 🧠 Backend Architecture

### Technologies
- Django 4  
- Django REST Framework  
- Django Channels  
- Redis  
- Pillow  
- Bleach  
- SimpleCaptcha  

### Key Components

#### Comments API
- List root comments with pagination  
- Return nested children  
- Create comment  
- Upload attachments  

#### Comments Serializer
```
class CommentSerializer:
    children = RecursiveSerializer(many=True)
```

#### XSS Filter
```
allowed_tags = ["a", "i", "strong", "code"]
```

#### Image Resizer
- Auto scales any large image to fit 320×240  

---

# 🎨 Frontend Architecture (Vue 3 + Vite)

### UI Components
| Component | Meaning |
|----------|---------|
| `App.vue` | Root SPA |
| `CommentForm.vue` | Comment creation form |
| `CommentItem.vue` | Single comment block |
| `CommentTree.vue` | Recursive renderer |
| `Preview.vue` | Preview window |
| `Lightbox.vue` | Image preview |

### Features Implemented
- State-preserving pagination  
- Dynamic sorting  
- File upload UI  
- HTML markup buttons `[i] [strong] [code] [a]`  
- Lightbox viewer  
- WebSocket auto-refresh  
- CAPTCHA rendering  

---

# 🐳 Running Project with Docker

### Build & Run
```
docker compose up --build
```

### Services
Backend → `http://localhost:8000`  
Frontend → `http://localhost:5173`  

### Create superuser
```
docker exec -it comments_backend python manage.py createsuperuser
```

---

# 🌐 API Endpoints (Full)

## GET /api/comments/
List paginated root comments:
```
{
  "count": 120,
  "next": "...",
  "previous": null,
  "results": [
      {
        "id": 1,
        "user_name": "...",
        "children": [...]
      }
  ]
}
```

## POST /api/comments/
Create a comment:
```
{
  "user_name": "alex",
  "email": "alex@gmail.com",
  "text": "Hello",
  "parent": null,
  "captcha_key": "...",
  "captcha_value": "..."
}
```

## POST /api/comments/<id>/upload/
Attach file.

---

# 🔧 Local Development Without Docker

### Backend
```
cd django_comments_spa
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

### Frontend
```
cd frontend
npm install
npm run dev
```

---

# ☁️ Deploying to AWS EC2

## 1. Launch EC2 instance
Ubuntu 22.04  
Open ports:
- 80, 443  
- 8000  
- 5173  
- 22  

## 2. Install Docker & Compose
```
sudo apt update
sudo apt install docker.io docker-compose -y
```

## 3. Clone project
```
git clone https://github.com/<your-repo>/django-comments-spa.git
cd django-comments-spa
```

## 4. Run production stack
```
docker compose up -d --build
```

## 5. Configure Nginx reverse proxy  
Routes example:
- `/api` → Django backend  
- `/ws` → Channels  
- `/` → Vue SPA build  

## 6. Enable HTTPS
```
sudo certbot --nginx
```

---

# 🔄 CI/CD With GitHub Actions

### `.github/workflows/deploy.yml`
Pipeline includes:
- SSH to EC2  
- Pull latest repo version  
- Rebuild containers  
- Restart services  

Supports **zero‑downtime deploy**.

---

# 🧪 Testing

```
python manage.py test
```

Covers:
- Recursive structure integrity  
- File validators  
- XSS sanitizing  
- Pagination behavior  
- CAPTCHA flow  
- WebSocket events  

---

# 📌 Requirements Checklist (All Completed)

| Requirement | Status |
|------------|--------|
| Unlimited nested comments | ✅ |
| Sorting root comments | ✅ |
| Pagination = 25/page | ✅ |
| XSS protection | ✅ |
| SQL injection protection | ✅ |
| Allowed HTML tags | ✅ |
| File validation + auto-resizing | ✅ |
| Lightbox effect | ✅ |
| CAPTCHA | ✅ |
| AJAX / SPA (no reloads) | ✅ |
| Preview before submit | ✅ |
| WebSockets real-time update | ✅ |
| Docker support | ✅ |
| AWS deployment | ✅ |
| CI/CD pipeline | ✅ |

---

# 🏁 Final Notes
This project is **fully production-ready**, with correct architecture, security, UI/UX, and deployment.

If you'd like, I can also generate:

✅ A **PDF** of this README  
✅ A **diagram (PNG/SVG)** of system architecture  
✅ A **fancy GitHub-styled README with badges**  
