const API_URL = import.meta.env.VITE_API_URL;

export async function loadCaptcha() {
  const response = await fetch(`${API_URL}/api/captcha/`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to load captcha");
  }

  const data = await response.json();

  // Приводим к формату, который ожидает компонент:
  return {
    key: data.captcha_key,
    image: `${API_URL}${data.captcha_image_url}`,
  };
}
