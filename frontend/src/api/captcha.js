// frontend/src/api/captcha.js

import { apiGet, buildUrl } from "./index";

/**
 * django-simple-captcha provides:
 * GET /captcha/refresh/
 * returns JSON like:
 * {
 *   "key": "...",
 *   "image_url": "/captcha/image/<hash>/"
 * }
 */
export async function loadCaptcha() {
  const data = await apiGet("/api/comments/captcha/");

  const key = data?.key || null;
  const imagePath = data?.image_url || data?.image || null; // fallback just in case
  const imageUrl = buildUrl(imagePath);

  return {
    key,
    image: imageUrl
      ? `${imageUrl}${imageUrl.includes("?") ? "&" : "?"}t=${Date.now()}`
      : null,
  };
}
