<template>
  <div class="comment-tree">
    <div
      v-for="comment in comments"
      :key="comment.id"
      class="comment-item"
      :id="`comment-${comment.id}`"
      :class="{
        'is-child': depth > 0,
        'scroll-highlight': highlightedId === comment.id,
      }"
    >
      <div class="comment-header">
        <div class="header-left">
          <strong class="user-name">{{ comment.user_name }}</strong>
          <span class="email">{{ comment.email }}</span>
        </div>

        <span class="date">{{ formatDate(comment.created_at) }}</span>
      </div>

      <div class="comment-text" v-html="renderText(comment.text)"></div>

      <!-- Attachments -->
      <div
        v-if="comment.attachments && comment.attachments.length"
        class="attachments"
      >
        <div v-for="a in comment.attachments" :key="a.id" class="attachment-item">
          <img
            v-if="isImageAttachment(a)"
            class="attachment-thumb"
            :src="resolveFileUrl(pickAttachmentFile(a))"
            alt="Attachment image"
            @click="openLightbox(resolveFileUrl(pickAttachmentFile(a)))"
          />

          <a
            v-else
            class="attachment-link"
            :href="resolveFileUrl(pickAttachmentFile(a))"
            target="_blank"
            rel="noopener noreferrer"
          >
            Download file
          </a>
        </div>
      </div>

      <!-- Actions -->
      <div class="comment-actions">
        <button type="button" class="reply-btn" @click="toggleReply(comment.id)">
          {{ replyTo === comment.id ? "Cancel reply" : "Reply" }}
        </button>

        <button
          v-if="isAdmin"
          type="button"
          class="delete-btn"
          :disabled="deletingId === comment.id"
          @click="onDelete(comment.id)"
        >
          {{ deletingId === comment.id ? "Deleting..." : "Delete" }}
        </button>
      </div>

      <div v-if="errorById[comment.id]" class="action-error">
        {{ errorById[comment.id] }}
      </div>

      <!-- Reply form -->
      <div v-if="replyTo === comment.id" class="reply-form">
        <CommentForm
          :me="me"
          :parent_id="comment.id"
          :reset-key="resetKey"
          @created="(payload) => handleCreated(payload, comment.id)"
        />
      </div>

      <!-- Children -->
      <div v-if="comment.children && comment.children.length" class="children">
        <CommentTree
          :comments="comment.children"
          :isAdmin="isAdmin"
          :me="me"
          :reset-key="resetKey"
          :depth="depth + 1"
          @changed="handleCreated"
        />
      </div>
    </div>

    <!-- Lightbox -->
    <div v-if="lightboxSrc" class="lightbox-overlay" @click="closeLightbox">
      <img :src="lightboxSrc" alt="Attachment preview" class="lightbox-image" />
      <button
        type="button"
        class="lightbox-close"
        @click.stop="closeLightbox"
        aria-label="Close"
      >
        ×
      </button>
    </div>
  </div>
</template>

<script>
import CommentForm from "./CommentForm.vue";
import { buildUrl } from "../api/index";
import { renderSafeHtml } from "../helpers/render";

/**
 * Admin delete helper.
 * We try a couple of common endpoints to be compatible with your backend variants.
 * - /api/comments/admin/comments/<id>/
 * - /api/comments/<id>/
 */
async function apiDeleteComment(commentId) {
  const token = localStorage.getItem("access");

  const headers = new Headers();
  headers.set("Accept", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const candidates = [
    `/api/comments/admin/comments/${commentId}/`,
    `/api/comments/${commentId}/`,
  ];

  let lastErr = null;

  for (const path of candidates) {
    const url = buildUrl(path);

    try {
      const res = await fetch(url, {
        method: "DELETE",
        credentials: "include",
        headers,
      });

      if (res.ok) return true;

      const ct = res.headers.get("content-type") || "";
      if (ct.includes("application/json")) {
        const data = await res.json().catch(() => null);
        const msg = data?.detail || JSON.stringify(data);
        const err = new Error(`HTTP ${res.status}`);
        err.status = res.status;
        err.payload = msg;
        lastErr = err;
        continue;
      }

      const text = await res.text().catch(() => "");
      const err = new Error(`HTTP ${res.status}`);
      err.status = res.status;
      err.payload = text;
      lastErr = err;
    } catch (e) {
      lastErr = e;
    }
  }

  throw lastErr || new Error("Failed to delete");
}

export default {
  name: "CommentTree",
  components: { CommentForm },

  props: {
    comments: { type: Array, required: true },
    isAdmin: { type: Boolean, default: false },
    me: { type: Object, default: null },
    resetKey: { type: Number, default: 0 },
    depth: { type: Number, default: 0 },
  },

  emits: ["changed"],

  data() {
    return {
      replyTo: null,

      // attachments preview
      lightboxSrc: null,

      // delete state
      deletingId: null,
      errorById: {},

      // scroll highlight
      highlightedId: null,
      _hlTimer: null,
    };
  },

  beforeUnmount() {
    if (this._hlTimer) clearTimeout(this._hlTimer);
  },

  methods: {
    // ---------- UI helpers ----------
    formatDate(value) {
      if (!value) return "";
      return new Date(value).toLocaleString();
    },

    renderText(text) {
      return renderSafeHtml(text || "");
    },

    resolveFileUrl(file) {
      if (!file) return "";
      if (String(file).startsWith("http://") || String(file).startsWith("https://")) {
        return file;
      }
      // backend often returns "/media/.."
      const p = String(file).startsWith("/") ? String(file) : `/${file}`;
      return buildUrl(p);
    },

    pickAttachmentFile(a) {
      // keep compatible with different serializer shapes
      return a?.file || a?.url || a?.file_url || "";
    },

    isImageAttachment(a) {
      const f = this.pickAttachmentFile(a);
      const lower = String(f).toLowerCase();
      return [".jpg", ".jpeg", ".png", ".gif", ".webp"].some((ext) =>
        lower.endsWith(ext)
      );
    },

    openLightbox(src) {
      if (src) this.lightboxSrc = src;
    },

    closeLightbox() {
      this.lightboxSrc = null;
    },

    toggleReply(commentId) {
      this.replyTo = this.replyTo === commentId ? null : commentId;
    },

    // ---------- Main "changed" flow ----------
    handleCreated(payloadOrNothing, parentIdFromTree) {
      // close reply form in current node
      this.replyTo = null;

      // bubble up to App.vue
      this.$emit("changed", payloadOrNothing);

      // scroll target:
      // prefer created comment id, fallback to parent
      const targetId =
        payloadOrNothing?.id ||
        payloadOrNothing?.commentId ||
        payloadOrNothing?.parentId ||
        payloadOrNothing?.parent_id ||
        parentIdFromTree ||
        null;

      if (!targetId) return;

      this.$nextTick(() => {
        const el = document.getElementById(`comment-${targetId}`);
        if (!el) return;

        el.scrollIntoView({ behavior: "smooth", block: "start" });

        this.highlightedId = targetId;
        if (this._hlTimer) clearTimeout(this._hlTimer);
        this._hlTimer = setTimeout(() => {
          this.highlightedId = null;
        }, 1200);
      });
    },

    // ---------- Admin delete ----------
    async onDelete(commentId) {
      if (!this.isAdmin) return;

      this.errorById = { ...this.errorById, [commentId]: "" };

      const ok = window.confirm("Delete this comment? This action cannot be undone.");
      if (!ok) return;

      this.deletingId = commentId;

      try {
        await apiDeleteComment(commentId);
        // tell App.vue to reload comments
        this.$emit("changed", { deletedId: commentId });
      } catch (e) {
        const msg =
          e?.payload ||
          (e?.status === 401 ? "Unauthorized" : "") ||
          (e?.status === 403 ? "Forbidden (admin only)" : "") ||
          "Failed to delete";
        this.errorById = { ...this.errorById, [commentId]: msg };
      } finally {
        this.deletingId = null;
      }
    },
  },
};
</script>

<style scoped>
.comment-tree {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comment-item {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  background: var(--surface-3);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
}

/* ✅ IMPORTANT: visually different children (replies) */
.comment-item.is-child {
  margin-left: 36px;
  padding: 12px 12px 12px 16px;
  border-left: 3px solid var(--border);
  background: var(--surface-2);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.14);
}

html[data-theme="light"] .comment-item.is-child {
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.08);
}


/* highlight after scroll */
.scroll-highlight {
  box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.35),
    0 10px 26px rgba(0, 0, 0, 0.18);
  border-color: rgba(96, 165, 250, 0.55);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

html[data-theme="light"] .comment-item {
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.1);
}

/* Header */
.comment-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.header-left {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 10px;
}

.user-name {
  font-weight: 900;
}

.email,
.date {
  color: var(--muted);
  font-size: 0.9rem;
}

.comment-text {
  margin: 10px 0 12px;
  line-height: 1.45;
  word-break: break-word;
}

/* Attachments */
.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 8px 0 10px;
}

.attachment-item {
  display: inline-flex;
  align-items: center;
}

.attachment-thumb {
  width: 160px;
  height: 120px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid var(--border);
  cursor: zoom-in;
  background: var(--input-bg);
}

.attachment-link {
  color: var(--primary);
  text-decoration: underline;
  font-weight: 800;
}

/* Actions */
.comment-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 6px;
}

.reply-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  border-radius: 14px;
  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.12);
  color: var(--text);
  cursor: pointer;
  font-weight: 900;
  min-width: 140px;
}
.reply-btn:hover {
  background: rgba(96, 165, 250, 0.18);
}
html[data-theme="light"] .reply-btn {
  background: rgba(37, 99, 235, 0.1);
  border-color: rgba(37, 99, 235, 0.3);
}
html[data-theme="light"] .reply-btn:hover {
  background: rgba(37, 99, 235, 0.14);
}

.delete-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border-radius: 14px;
  border: 1px solid rgba(248, 113, 113, 0.45);
  background: rgba(248, 113, 113, 0.12);
  color: var(--text);
  cursor: pointer;
  font-weight: 900;
  min-width: 110px;
}
.delete-btn:hover {
  background: rgba(248, 113, 113, 0.18);
}
.delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-error {
  margin-top: 8px;
  text-align: center;
  color: var(--danger, #ef4444);
  font-weight: 800;
}

.reply-form {
  margin-top: 12px;
  padding: 12px;
  border-radius: 16px;
  background: var(--surface-2);
  border: 1px solid var(--border);
}

.children {
  margin-top: 12px;
}

/* Lightbox */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.78);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 18px;
}

.lightbox-image {
  max-width: min(1100px, 95vw);
  max-height: 90vh;
  border-radius: 14px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.45);
}

.lightbox-close {
  position: fixed;
  top: 18px;
  right: 18px;
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 26px;
  line-height: 44px;
  cursor: pointer;
}
</style>
