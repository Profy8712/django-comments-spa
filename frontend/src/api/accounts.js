import { apiGet } from "./index";

/**
 * GET /api/accounts/me/
 * Returns current user info (includes is_staff / is_superuser).
 */
export function fetchMe() {
  return apiGet("/api/accounts/me/");
}
