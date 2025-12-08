// frontend/src/api/attachments.js
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Upload a single attachment for the given comment.
 * Backend URL: POST /api/comments/<id>/upload/
 */
export async function uploadAttachment(commentId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const resp = await fetch(`${API_URL}/api/comments/${commentId}/upload/`, {
    method: "POST",
    body: formData,
  });

  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(
      `Failed to upload attachment (status ${resp.status}): ${text}`,
    );
  }

  return await resp.json();
}
