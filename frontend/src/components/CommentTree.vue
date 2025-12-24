<template>
  <div class="comment-tree">
    <div v-for="comment in comments" :key="comment.id" class="comment-item">
      <div class="comment-header">
        <strong class="user-name">{{ comment.user_name }}</strong>
        <span class="email">{{ comment.email }}</span>
        <span class="date">{{ formatDate(comment.created_at) }}</span>
      </div>

      <div class="comment-text" v-html="renderText(comment.text)"></div>

      <div
        v-if="comment.attachments && comment.attachments.length"
        class="attachments"
      >
        <div
          v-for="a in comment.attachments"
          :key="a.id"
          class="attachment-item"
        >
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

      <button type="button" class="reply-btn" @click="toggleReply(comment.id)">
        {{ replyTo === comment.id ? "Cancel reply" : "Reply" }}
      </button>

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
    comments: {
      type: Array,
      required: true,
    },
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
      const date = new Date(value);
      return date.toLocaleString();
    },

    openLightbox(src) {
      if (!src) return;
      this.lightboxSrc = src;
    },

    closeLightbox() {
      this.lightboxSrc = null;
    },

        resolveFileUrl(file) {
        if (!file) return "";

        // If backend already returned absolute URL — use it as-is
        if (file.startsWith("http://") || file.startsWith("https://")) {
          return file;
        }

        // Otherwise build absolute URL
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

.comment-item {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px;
  background: #fff;
}

.comment-header {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 8px;
}

.user-name {
  font-weight: 700;
}

.email {
  color: #6b7280;
  font-size: 0.9rem;
}

.date {
  margin-left: auto;
  color: #6b7280;
  font-size: 0.85rem;
}

.comment-text {
  margin: 8px 0 10px;
  line-height: 1.35;
  word-break: break-word;
}

.attachments {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 8px 0 10px;
}

.attachment-item {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.attachment-thumb {
  width: 160px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  cursor: zoom-in;
}

.attachment-link {
  color: #2563eb;
  text-decoration: underline;
}

.reply-btn {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  cursor: pointer;
}

.reply-form {
  margin-top: 10px;
  padding: 10px;
  border-radius: 10px;
  background: #f9fafb;
  border: 1px solid #eef2f7;
}

.children {
  margin-top: 12px;
  padding-left: 14px;
  border-left: 2px solid #eef2f7;
}

.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 18px;
}

.lightbox-image {
  max-width: min(1100px, 95vw);
  max-height: 90vh;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}

.lightbox-close {
  position: fixed;
  top: 18px;
  right: 18px;
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: none;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  font-size: 26px;
  line-height: 44px;
  cursor: pointer;
}
</style>
