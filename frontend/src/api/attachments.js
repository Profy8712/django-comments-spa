// frontend/src/api/attachments.js

import { apiPostForm } from "./index";
import { getAccessToken } from "./auth";

export function uploadAttachment(commentId, file) {
  if (!commentId) throw new Error("commentId is required");
  if (!file) throw new Error("file is required");

  // Hard guard: anonymous must NOT upload files
  const token = getAccessToken();
  if (!token) {
    const err = new Error("Attachments are allowed only for authenticated users.");
    err.status = 401;
    throw err;
  }

  const formData = new FormData();
  formData.append("file", file);

  // Your backend route:
  return apiPostForm(`/api/comments/${commentId}/upload/`, formData);
}
