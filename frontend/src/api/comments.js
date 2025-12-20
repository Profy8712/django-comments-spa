// frontend/src/api/comments.js

import { apiGet, apiPostJson } from "./index";

function hasToken() {
  const t = localStorage.getItem("access");
  return !!(t && t.trim());
}

export function fetchComments(page = 1, ordering = "-created_at") {
  const params = new URLSearchParams();
  params.set("page", String(page));
  if (ordering) params.set("ordering", String(ordering));

  return apiGet(`/api/comments/?${params.toString()}`);
}

export function createComment(data, parentId = null) {
  const payload = { ...data };
  if (parentId) payload.parent = parentId;

  // If JWT exists -> do NOT send captcha fields at all
  if (hasToken()) {
    delete payload.captcha_key;
    delete payload.captcha_value;
  }

  return apiPostJson("/api/comments/", payload);
}
