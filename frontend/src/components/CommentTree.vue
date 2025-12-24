<template>
  <div class="comment-tree">
    <div v-for="comment in comments" :key="comment.id" class="comment-item">
      <div class="comment-header">
        <div class="header-left">
          <strong class="user-name">{{ comment.user_name }}</strong>
          <span class="email">{{ comment.email }}</span>
        </div>
        <span class="date">{{ formatDate(comment.created_at) }}</span>
      </div>

      <div class="comment-text" v-html="renderText(comment.text)"></div>

      <div v-if="comment.attachments && comment.attachments.length" class="attachments">
        <div v-for="a in comment.attachments" :key="a.id" class="attachment-item">
          <img
            v-if="isImageAttachment(a)"
            class="attachment-thumb"
            :src="resolveFileUrl(a.file)"
            alt="Attachment image"
            @click="openLightbox(resolveFileUrl(a.file))"
          />

          <a
            v-else
            class="attachment-link"
            :href="resolveFileUrl(a.file)"
            target="_blank"
            rel="noopener noreferrer"
          >
            Download file
          </a>
        </div>
      </div>

      <div class="comment-actions">
        <button type="button" class="reply-btn" @click="toggleReply(comment.id)">
          {{ replyTo === comment.id ? "Cancel reply" : "Reply" }}
        </button>
      </div>

      <div v-if="replyTo === comment.id" class="reply-form">
        <CommentForm :parent_id="comment.id" @created="handleCreated" />
      </div>

      <div v-if="comment.children && comment.children.length" class="children">
        <CommentTree :comments="comment.children" @changed="handleCreated" />
      </div>
    </div>

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

export default {
  name: "CommentTree",
  components: { CommentForm },
  props: {
    comments: { type: Array, required: true },
  },
  emits: ["changed"],
  data() {
    return {
      replyTo: null,
      lightboxSrc: null,
    };
  },
  methods: {
    async handleCreated() {
      this.replyTo = null;
      this.$emit("changed");
    },

    toggleReply(commentId) {
      this.replyTo = this.replyTo === commentId ? null : commentId;
    },

    formatDate(value) {
      if (!value) return "";
      return new Date(value).toLocaleString();
    },

    openLightbox(src) {
      if (src) this.lightboxSrc = src;
    },

    closeLightbox() {
      this.lightboxSrc = null;
    },

    resolveFileUrl(file) {
      if (!file) return "";
      if (file.startsWith("http://") || file.startsWith("https://")) return file;
      return buildUrl(file.startsWith("/") ? file : `/${file}`);
    },

    isImageAttachment(attachment) {
      const f = attachment?.file || "";
      const lower = String(f).toLowerCase();
      const exts = [".jpg", ".jpeg", ".png", ".gif", ".webp"];
      return exts.some((ext) => lower.endsWith(ext));
    },

    renderText(text) {
      return renderSafeHtml(text || "");
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

/* Card (base = uses variables; light becomes solid) */
.comment-item {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  background: var(--surface-3);
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
}

/* Dark keeps "glassy" look without affecting text */
html:not([data-theme="light"]) .comment-item {
  background: rgba(17, 28, 51, 0.75);
}

/* In light, shadow should be softer */
html[data-theme="light"] .comment-item {
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.10);
}

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

.email {
  color: var(--muted);
  font-size: 0.92rem;
}

.date {
  color: var(--muted);
  font-size: 0.88rem;
  white-space: nowrap;
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
  margin-top: 6px;
}

/* Reply button */
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
  background: rgba(37, 99, 235, 0.10);
  border-color: rgba(37, 99, 235, 0.30);
}

html[data-theme="light"] .reply-btn:hover {
  background: rgba(37, 99, 235, 0.14);
}

/* Reply form panel (NO fog in light) */
.reply-form {
  margin-top: 12px;
  padding: 12px;
  border-radius: 16px;
  background: var(--surface-2);
  border: 1px solid var(--border);
}

/* Dark keeps old tone */
html:not([data-theme="light"]) .reply-form {
  background: rgba(15, 23, 42, 0.60);
}

/* Children indentation line */
.children {
  margin-top: 12px;
  padding-left: 14px;
  border-left: 2px solid var(--border);
}

/* Dark keeps stronger line */
html:not([data-theme="light"]) .children {
  border-left-color: rgba(34, 48, 74, 0.7);
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
  background: rgba(255, 255, 255, 0.10);
  color: #fff;
  font-size: 26px;
  line-height: 44px;
  cursor: pointer;
}
</style>
