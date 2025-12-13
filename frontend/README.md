
# Frontend — Django Comments SPA (Vue 3 + Vite)

This directory contains the Single Page Application (SPA) frontend for the Django Comments SPA project.

---

## Technologies
- Vue 3 (Composition API)
- Vite
- Fetch API
- WebSockets
- Lightbox
- CSS3

---

## Directory Structure

frontend/
- src/
  - api/
  - components/
  - helpers/
  - App.vue
  - main.js
- public/
- index.html
- package.json
- vite.config.js

---

## Features
- Nested comments (recursive rendering)
- Sorting and pagination
- File uploads
- Lightbox image preview
- CAPTCHA validation
- Preview before submit
- WebSocket real-time updates
- XSS-safe rendering

---

## Development

Install dependencies:
npm install

Run dev server:
npm run dev

Frontend runs at http://localhost:5173

Backend should be running at http://localhost:8000

---

## Docker

Frontend is started automatically via docker-compose.

---

## Production Build

npm run build

---

## Notes
Production-ready frontend SPA.
