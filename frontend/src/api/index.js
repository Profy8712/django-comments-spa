export async function apiGet(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`GET ${url} failed with status ${response.status}`);
  }
  return await response.json();
}

export async function apiPost(url, data) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const payload = await response.json();

  if (!response.ok) {
    throw payload;
  }

  return payload;
}

export function fetchComments(page = 1, ordering = "-created_at") {
  const params = new URLSearchParams({
    page: String(page),
    ordering,
  });
  return apiGet(`/api/comments/?${params.toString()}`);
}

export function fetchCaptcha() {
  return apiGet("/api/captcha/");
}

export function createComment(data) {
  return apiPost("/api/comments/", data);
}

// backend base URL for media files (attachments)
export const BACKEND_URL = "http://127.0.0.1:8000";
