// Base URL of the backend API and media server.
// In Docker environment, replace with: "http://comments_backend:8000"
export const BACKEND_URL = "http://127.0.0.1:8000";

/**
 * Builds a full URL for API calls.
 * If the path already contains a protocol (http/https), it will be used as-is.
 * Otherwise it will be prefixed with BACKEND_URL.
 */
function buildUrl(path) {
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  return `${BACKEND_URL}${path}`;
}

/**
 * Sends a GET request to the backend API.
 * Throws an error if the request fails.
 */
export async function apiGet(path) {
  const url = buildUrl(path);

  const response = await fetch(url, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`GET ${url} failed with status ${response.status}`);
  }

  return await response.json();
}

/**
 * Sends a POST request with JSON payload.
 * Returns JSON or throws backend validation errors.
 */
export async function apiPost(path, data) {
  const url = buildUrl(path);

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(data),
  });

  const payload = await response.json();

  if (!response.ok) {
    throw payload;
  }

  return payload;
}

/**
 * Fetch paginated and ordered comments.
 */
export function fetchComments(page = 1, ordering = "-created_at") {
  const params = new URLSearchParams({
    page: String(page),
    ordering,
  });

  return apiGet(`/api/comments/?${params.toString()}`);
}

/**
 * Fetch new CAPTCHA pair (key + image URL).
 */
export function fetchCaptcha() {
  return apiGet("/api/captcha/");
}

/**
 * Create a new comment via POST request.
 */
export function createComment(data) {
  return apiPost("/api/comments/", data);
}
