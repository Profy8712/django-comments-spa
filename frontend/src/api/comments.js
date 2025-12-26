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
  const params = new URLSearchParams();
  params.set("page", String(page));
  if (ordering) params.set("ordering", String(ordering));

  return apiGet(`/api/comments/?${params.toString()}`);
}

export function createComment(data, parentId = null) {
  const payload = { ...(data || {}) };

  // Reply support:
  // - if payload already has parent_id or parent -> use it
  // - else use optional parentId arg
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
