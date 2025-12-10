# Django Comments SPA

Single Page Application for a threaded comments system built with **Django + DRF + Channels** on the backend and **Vue 3 + Vite** on the frontend.

Users can:

- Post new comments with basic formatting  
- Reply to existing comments (nested / threaded tree)  
- Attach images and text files  
- Pass CAPTCHA validation  
- See new comments in real time via WebSockets  
- Sort and paginate comments  

The project is fully containerised with **Docker** and can be deployed to a VDS/Cloud server (e.g. AWS EC2) with optional **CI/CD via GitHub Actions**.

---

## Tech stack

**Backend**

- Python 3.12  
- Django  
- Django REST Framework  
- Django Channels  
- django-simple-captcha  
- Pillow  
- SQLite (default demo DB)

**Frontend**

- Vue 3  
- Vite  

**DevOps**

- Docker, Docker Compose  
- GitHub Actions  
- AWS EC2

---

## Features

- Comment model with nested replies (`parent` FK)
- Attachments with automatic image resizing
- TXT size validation (100 KB)
- CAPTCHA validation
- Pagination & ordering
- WebSocket real-time updates
- SPA with reply forms, previews, lightbox, and formatting buttons

---

## Running locally (Docker)

```bash
docker compose up --build
```

Backend: http://127.0.0.1:8000  
Frontend: http://localhost:5173  

---

## Backend .env example

```
DJANGO_SECRET_KEY=dev-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,comments_backend
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173
```

---

## Frontend .env

```
VITE_API_URL=http://127.0.0.1:8000
```

---

## Production deployment (AWS EC2)

### 1. Create EC2 instance  
Ubuntu 22.04 recommended.

### 2. Install Docker

```bash
curl -fsSL https://get.docker.com | sudo sh
```

### 3. Clone project on server

```bash
git clone https://github.com/YourRepo/django-comments-spa.git
cd django-comments-spa
```

### 4. Create production env files

`backend/.env.prod`:

```
DJANGO_SECRET_KEY=your-prod-key
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=your-domain.com,YOUR_EC2_IP
DJANGO_CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

`frontend/.env.production`:

```
VITE_API_URL=https://your-backend-domain.com
```

### 5. Build & run

```bash
docker compose up -d --build
```

---

## CI/CD (GitHub Actions → EC2)

### Required GitHub Secrets

- `EC2_HOST`
- `EC2_USER`
- `EC2_SSH_KEY`
- `EC2_PROJECT_PATH`

### `.github/workflows/deploy.yml`

```yaml
name: Deploy to EC2

on:
  push:
    branches: [ "main" ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: ${{ secrets.EC2_SSH_KEY }}

      - name: Deploy
        run: |
          ssh -o StrictHostKeyChecking=no ${{ secrets.EC2_USER }}@${{ secrets.EC2_HOST }} << 'EOF'
            cd ${{ secrets.EC2_PROJECT_PATH }}
            git pull origin main
            docker compose up -d --build
            docker image prune -f
          EOF
```

---

## Notes

- For production, consider Redis + PostgreSQL  
- For HTTPS, place Nginx or Caddy reverse proxy in front of the backend

---

## License

MIT

