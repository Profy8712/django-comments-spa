<template>
  <div class="comment-tree">
    <div
      v-for="comment in comments"
      :key="comment.id"
      class="comment-item"
    >
      <div class="comment-header">
        <strong class="user-name">{{ comment.user_name }}</strong>
        <span class="email">{{ comment.email }}</span>
        <span class="date">{{ formatDate(comment.created_at) }}</span>
      </div>

      <div
        class="comment-text"
        v-html="renderText(comment.text)"
      ></div>

      <div
        v-if="comment.attachments && comment.attachments.length"
        class="attachments"
      >
        <div
          v-for="a in comment.attachments"
          :key="a.id"
          class="attachment-item"
        >
          <!-- image preview with lightbox -->
          <img
            v-if="isImageAttachment(a)"
            class="attachment-thumb"
            :src="resolveFileUrl(a.file)"
            alt="Attachment image"
            @click="openLightbox(resolveFileUrl(a.file))"
          />

          <!-- non-image file -->
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

      <button
        type="button"
        class="reply-btn"
        @click="toggleReply(comment.id)"
      >
        {{ replyTo === comment.id ? "Cancel reply" : "Reply" }}
      </button>

      <div v-if="replyTo === comment.id" class="reply-form">
        <CommentForm @created="handleCreated" />
      </div>

      <div
        v-if="comment.children && comment.children.length"
        class="children"
      >
        <CommentTree
          :comments="comment.children"
          @changed="handleCreated"
        />
      </div>
    </div>

    <!-- lightbox overlay -->
    <div
      v-if="lightboxSrc"
      class="lightbox-overlay"
      @click="closeLightbox"
    >
      <img
        :src="lightboxSrc"
        alt="Attachment preview"
        class="lightbox-image"
      />
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
import { BACKEND_URL } from "../api";
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
      backendUrl: BACKEND_URL,
      lightboxSrc: null,
    };
  },
  methods: {
    formatDate(value) {
      if (!value) return "";
      const date = new Date(value);
      return date.toLocaleString();
    },
    toggleReply(id) {
      this.replyTo = this.replyTo === id ? null : id;
    },
    handleCreated() {
      this.replyTo = null;
      this.$emit("changed");
    },
    renderText(text) {
      return renderSafeHtml(text || "");
    },
    resolveFileUrl(file) {
      if (!file) return "";
      if (file.startsWith("http://") || file.startsWith("https://")) {
        return file;
      }
      if (file.startsWith("/")) {
        return `${this.backendUrl}${file}`;
      }
      return `${this.backendUrl}/${file}`;
    },
    isImageAttachment(attachment) {
      if (!attachment || !attachment.file) return false;
      const lower = attachment.file.toLowerCase();
      const exts = [".jpg", ".jpeg", ".png", ".gif"];
      return exts.some((ext) => lower.endsWith(ext));
    },
    openLightbox(src) {
      this.lightboxSrc = src;
    },
    closeLightbox() {
      this.lightboxSrc = null;
    },
  },
};
</script>

<style scoped>
.comment-tree {
  margin-top: 1.5rem;
}

.comment-item {
  border: 1px solid #e5e7eb;
  padding: 0.9rem 1rem;
  margin-bottom: 0.9rem;
  border-radius: 10px;
  background-color: #ffffff;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.04);
}

.comment-header {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  font-size: 0.9rem;
  margin-bottom: 0.35rem;
}

.user-name {
  font-weight: 600;
}

.email {
  color: #6b7280;
}

.date {
  margin-left: auto;
  font-size: 0.8rem;
  color: #9ca3af;
}

.comment-text {
  margin: 0.35rem 0 0.6rem;
  font-size: 0.95rem;
  line-height: 1.5;
}

.attachments {
  margin-bottom: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.attachment-item {
  display: inline-flex;
  align-items: center;
}

.attachment-thumb {
  max-width: 130px;
  max-height: 130px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #e5e7eb;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.attachment-thumb:hover {
  transform: scale(1.04);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
}

.attachment-link {
  font-size: 0.85rem;
  color: #2563eb;
  text-decoration: underline;
}

.reply-btn {
  font-size: 0.85rem;
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background-color: #f9fafb;
  cursor: pointer;
}

.reply-btn:hover {
  background-color: #e5f0ff;
}

.children {
  margin-left: 1.5rem;
  padding-left: 0.75rem;
  border-left: 2px solid #f3f4f6;
  margin-top: 0.7rem;
}

/* lightbox styles */

.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.lightbox-image {
  max-width: 90%;
  max-height: 90%;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.lightbox-close {
  position: absolute;
  top: 20px;
  right: 30px;
  font-size: 2.5rem;
  background: transparent;
  border: none;
  color: #f9fafb;
  cursor: pointer;
  line-height: 1;
}
</style>
