const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function loadCaptcha() {
  const resp = await fetch(`${API_URL}/api/captcha/`, {
    credentials: "include",
  });

  if (!resp.ok) {
    throw new Error("Failed to load CAPTCHA");
  }

  const data = await resp.json(); // { key, image }

  let imageUrl = data.image;
  if (imageUrl.startsWith("/")) {
    imageUrl = `${API_URL}${imageUrl}`;
  }

  return {
    key: data.key,
    image: imageUrl,
  };
}
