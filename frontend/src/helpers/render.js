// src/helpers/render.js

export function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function sanitizeUrl(url) {
  const trimmed = String(url || "").trim();
  if (!trimmed) {
    return "";
  }

  const lowered = trimmed.toLowerCase();

  // Block dangerous protocols
  if (lowered.startsWith("javascript:") || lowered.startsWith("data:")) {
    return "";
  }

  return trimmed;
}

/**
 * Convert pseudo-tags in plain text into a very small
 * safe subset of HTML. Everything else is escaped.
 *
 * Supported pseudo-tags:
 * - [i]...[/i]
 * - [strong]...[/strong]
 * - [code]...[/code]
 * - [a href="..."]text[/a] or [a]url[/a]
 */
export function renderSafeHtml(rawText) {
  if (!rawText) {
    return "";
  }

  let safe = escapeHtml(rawText);

  // [i]...[/i]
  safe = safe.replace(/\[i](.+?)\[\/i]/gis, "<i>$1</i>");

  // [strong]...[/strong]
  safe = safe.replace(/\[strong](.+?)\[\/strong]/gis, "<strong>$1</strong>");

  // [code]...[/code]
  safe = safe.replace(/\[code](.+?)\[\/code]/gis, "<code>$1</code>");

  // [a href="..."]text[/a] or [a]url[/a]
  safe = safe.replace(
    /\[a(?:\s+href="([^"]*)")?](.+?)\[\/a]/gis,
    (_, href, text) => {
      const url = sanitizeUrl(href || text);
      const content = escapeHtml(text || "");

      if (!url) {
        return content;
      }

      return `<a href="${url}" rel="nofollow noopener" target="_blank">${content}</a>`;
    }
  );

  return safe;
}
