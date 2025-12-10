export function escapeHtml(text) {
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return text.replace(/[&<>"']/g, (m) => map[m]);
}

export function applyPseudoTags(text) {
  // Allowed pseudo tags converted to safe HTML
  return text
    .replace(/\[i\](.*?)\[\/i\]/gis, "<i>$1</i>")
    .replace(/\[strong\](.*?)\[\/strong\]/gis, "<strong>$1</strong>")
    .replace(/\[code\](.*?)\[\/code\]/gis, "<code>$1</code>")
    .replace(
      /\[a href=['"](.*?)['"]\](.*?)\[\/a\]/gis,
      '<a href="$1" target="_blank" rel="noopener noreferrer">$2</a>'
    );
}

export function renderSafeHtml(text) {
  if (!text) return "";
  const escaped = escapeHtml(text);
  return applyPseudoTags(escaped);
}
