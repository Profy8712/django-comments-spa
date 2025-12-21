// frontend/src/api/captcha.js
import { apiGet, buildUrl } from "./index";

/**
 * Backend endpoint:
 * GET /api/comments/captcha/
 * Response example:
 * {
 *   "key": "...",
 *   "image_url": "/captcha/image/<hash>/"
 * }
 */
export async function loadCaptcha() {
  const data = await apiGet("/api/comments/captcha/");

  const key = data?.key ?? null;

  // Backend may return image_url or image
  const imagePath = data?.image_url ?? data?.image ?? null;

  // "/captcha/image/..." -> absolute URL based on API_URL (VITE_API_URL)
  const abs = imagePath ? buildUrl(imagePath) : null;

  // cache-buster to avoid browser caching
  const image = abs
    ? `${abs}${abs.includes("?") ? "&" : "?"}t=${Date.now()}`
    : null;

  return { key, image };
}

// Backward-compatible alias (если где-то в проекте осталось старое имя)
export const loadCaptchaApi = loadCaptcha;
