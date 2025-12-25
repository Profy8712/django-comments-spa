// frontend/src/api/accounts.js
import { apiGet, getAccessToken } from "./index";

/**
 * GET /api/accounts/me/
 * Returns current user info (includes is_staff / is_superuser).
 *
 * IMPORTANT:
 * - Do NOT call backend if token is missing (prevents 401 spam after logout).
 */
export async function fetchMe() {
  const token = getAccessToken();
  if (!token) return null;
  return apiGet("/api/accounts/me/");
}
