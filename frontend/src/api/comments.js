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

/**
 * If your backend supports multipart to /api/comments/ for creating comment with files.
 * Keep as-is to not break current flows.
 */
export function createCommentWithFiles(formData) {
  return apiPostForm("/api/comments/", formData);
}

/**
 * Variant C: upload files first, then create comment with attachment_ids + upload_key.
 * Endpoint must exist on backend: POST /api/comments/upload/
 */
export async function uploadFiles(files) {
  const uploaded = [];

  for (const file of files || []) {
    const fd = new FormData();
    fd.append("file", file);
    const one = await apiPostForm("/api/comments/upload/", fd);
    uploaded.push(one);
  }

  const attachment_ids = uploaded.map((x) => x.id);
  const upload_key = uploaded[0]?.upload_key || null;
  return { attachment_ids, upload_key, uploaded };
}

/** delete comment (normal endpoint) */
export function deleteComment(id) {
  if (!id) throw new Error("deleteComment: id is required");
  return apiDelete(`/api/comments/${id}/`);
}

/**
 * Admin-only delete endpoint:
 * DELETE /api/comments/admin/comments/<id>/
 */
export function adminDeleteComment(commentId) {
  if (!commentId) throw new Error("commentId is required");
  return apiDelete(`/api/comments/admin/comments/${commentId}/`);
}
