const API_URL = import.meta.env.VITE_API_URL;

export async function uploadAttachment(commentId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_URL}/api/comments/${commentId}/attachments/`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(
      text || `Failed to upload attachment for comment ${commentId}`
    );
  }

  return await response.json();
}
