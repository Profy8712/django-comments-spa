// frontend/src/api/index.js

const API_URL =
  import.meta.env.VITE_API_URL ||
  `${window.location.protocol}//${window.location.host}`;

export function getApiBase() {
  return API_URL;
}

/**
 * Build absolute URL:
 * - absolute http(s) stays unchanged
 * - adds leading "/" if missing
 */
export function buildUrl(path) {
  if (!path) return path;

  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }

  const p = path.startsWith("/") ? path : `/${path}`;
  return `${API_URL}${p}`;
}

/** Token helpers */
export function getAccessToken() {
  const t = localStorage.getItem("access");
  return t && t.trim() ? t.trim() : null;
}

export function clearTokens() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
}

/**
 * Low-level request helper:
 * - adds Authorization if token exists (and withAuth=true)
 * - sends cookies (credentials include)
 * - if server returns 401 -> clear tokens and retry once WITHOUT Authorization
 */
async function request(path, options = {}, { withAuth = true, retryOn401 = true } = {}) {
  const url = buildUrl(path);

  const headers = new Headers(options.headers || {});
  const token = withAuth ? getAccessToken() : null;

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (!headers.has("Accept")) headers.set("Accept", "application/json");

  const res = await fetch(url, {
    credentials: "include",
    ...options,
    headers,
  });

  if (res.status === 401 && retryOn401) {
    // Token invalid/expired -> switch to anonymous and retry once
    clearTokens();

    const retryHeaders = new Headers(headers);
    retryHeaders.delete("Authorization");

    return fetch(url, {
      credentials: "include",
      ...options,
      headers: retryHeaders,
    });
  }

  return res;
}

async function readPayload(res) {
  const ct = res.headers.get("content-type") || "";
  const isJson = ct.includes("application/json");

  if (isJson) {
    const data = await res.json().catch(() => null);
    return { data, text: null };
  }

  const text = await res.text().catch(() => "");
  return { data: null, text };
}

function makeError(res, payload) {
  const err = new Error(`HTTP ${res.status}`);
  err.status = res.status;
  err.payload = payload;
  return err;
}

export async function apiGet(path, opts = {}) {
  const res = await request(path, { method: "GET", ...opts }, { withAuth: true, retryOn401: true });
  const payload = await readPayload(res);

  if (!res.ok) throw makeError(res, payload.data ?? payload.text);
  return payload.data ?? payload.text;
}

export async function apiPostJson(path, data, opts = {}) {
  const res = await request(
    path,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(opts.headers || {}),
      },
      body: JSON.stringify(data ?? {}),
      ...opts,
    },
    { withAuth: true, retryOn401: true }
  );

  const payload = await readPayload(res);
  if (!res.ok) throw makeError(res, payload.data ?? payload.text);
  return payload.data ?? payload.text;
}

export async function apiPostForm(path, formData, opts = {}) {
  // NOTE: do not set Content-Type for FormData (browser sets boundary)
  const res = await request(
    path,
    {
      method: "POST",
      body: formData,
      ...opts,
    },
    { withAuth: true, retryOn401: true }
  );

  const payload = await readPayload(res);
  if (!res.ok) throw makeError(res, payload.data ?? payload.text);
  return payload.data ?? payload.text;
}
