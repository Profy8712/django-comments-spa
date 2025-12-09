const API_URL = import.meta.env.VITE_API_URL;

export async function fetchComments(page = 1, ordering = "-created_at") {
  const params = new URLSearchParams({
    page: String(page),
    ordering,
  });

  const response = await fetch(`${API_URL}/api/comments/?${params.toString()}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch comments: ${response.status}`);
  }

  return await response.json();
}

export async function createComment(payload) {
  const response = await fetch(`${API_URL}/api/comments/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let errorDetail = "Failed to create comment";

    try {
      const data = await response.json();
      if (data.detail) {
        errorDetail = data.detail;
      }
    } catch (e) {
      // ignore parse error
    }

    throw new Error(errorDetail);
  }

  return await response.json();
}
