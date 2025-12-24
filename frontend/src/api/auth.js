// frontend/src/api/auth.js
import { buildUrl } from "./index";

const ACCESS_KEY = "access";
const REFRESH_KEY = "refresh";

export function getAccessToken() {
  const t = localStorage.getItem(ACCESS_KEY);
  return t && t.trim() ? t.trim() : null;
}

export function getRefreshToken() {
  const t = localStorage.getItem(REFRESH_KEY);
  return t && t.trim() ? t.trim() : null;
}

export function isAuthed() {
  return !!getAccessToken();
}

export function setTokens({ access, refresh }) {
  if (access) localStorage.setItem(ACCESS_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  window.dispatchEvent(new Event("auth-changed"));
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  window.dispatchEvent(new Event("auth-changed"));
}

export async function login(username, password) {
  const url = buildUrl("/api/auth/token/");

  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });

  let data = null;
  try {
    data = await r.json();
  } catch (_) {
    // ignore
  }

  if (!r.ok) {
    const msg =
      (data && (data.detail || data.message)) ||
      `Login failed (HTTP ${r.status})`;
    throw new Error(msg);
  }

  if (!data || !data.access) {
    throw new Error("Login failed: no access token in response");
  }

  setTokens({ access: data.access, refresh: data.refresh });
  return data;
}

export function logout() {
  clearTokens();
}
