// frontend/src/api/comments.js
import { apiGet, apiPostJson } from "./index";

function getAccessToken() {
  const t = localStorage.getItem("access");
  return t && t.trim() ? t.trim() : null;
}

function hasToken() {
  return !!getAccessToken();
}

function normalizeParentId(parentId) {
  if (parentId === null || parentId === undefined || parentId === "") return null;
  const n = Number(parentId);
  return Number.isFinite(n) ? n : null;
}

export function fetchComments(page = 1, ordering = "-created_at") {
  // ✅ guard: avoid ?page=[object Object] -> "Invalid page."
  const p = Number(page);
  const safePage = Number.isFinite(p) && p > 0 ? p : 1;

  const params = new URLSearchParams();
  params.set("page", String(safePage));
  if (ordering) params.set("ordering", String(ordering));

  return apiGet(`/api/comments/?${params.toString()}`);
}

export function createComment(data, parentId = null) {
  const payload = { ...(data || {}) };

  const pidFromPayload = normalizeParentId(payload.parent_id ?? payload.parent ?? null);
  const pidFromArg = normalizeParentId(parentId);
  const pid = pidFromPayload !== null ? pidFromPayload : pidFromArg;

  if (pid !== null) {
    payload.parent = pid;
    delete payload.parent_id;
  } else {
    delete payload.parent;
    delete payload.parent_id;
  }

  // If JWT exists -> do NOT send captcha fields at all
  if (hasToken()) {
    delete payload.captcha_key;
    delete payload.captcha_value;
  }

  return apiPostJson("/api/comments/", payload);
}
