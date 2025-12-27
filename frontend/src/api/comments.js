// frontend/src/api/comments.js
import { apiGet, apiPostJson, apiPostForm, apiDelete } from "./index";

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

/** ✅ If you have upload endpoint */
export function createCommentWithFiles(formData) {
  // In your project you likely post to /api/comments/ as multipart
  // This should exist only if your backend supports it.
  return apiPostForm("/api/comments/", formData);
}

/** ✅ NEW: delete comment */
export function deleteComment(id) {
  if (!id) throw new Error("deleteComment: id is required");
  return apiDelete(`/api/comments/${id}/`);
}


// Admin-only delete endpoint:
// DELETE /api/comments/admin/comments/<id>/
export function adminDeleteComment(commentId) {
  if (!commentId) throw new Error("commentId is required");
  return apiDelete(`/api/comments/admin/comments/${commentId}/`);
}
