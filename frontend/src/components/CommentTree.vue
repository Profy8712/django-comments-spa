<template>
  <div class="comment-tree">
    <div v-for="comment in comments" :key="comment.id" class="comment-item">
      <div class="comment-header">
        <strong>{{ comment.user_name }}</strong>
        <span class="email">{{ comment.email }}</span>
        <span class="date">{{ formatDate(comment.created_at) }}</span>
      </div>

      <div
        class="comment-text"
        v-html="comment.text"
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
          <template v-if="isImage(a)">
            <img
              :src="backendUrl + a.file"
              alt="Attachment image"
              class="attachment-thumb"
              @click="openLightbox(backendUrl + a.file)"
            />
          </template>

          <template v-else>
            <a
              :href="backendUrl + a.file"
              target="_blank"
              rel="noopener noreferrer"
            >
              Download file
            </a>
          </template>
        </div>
      </div>

      <button class="reply-btn" @click="toggleReply(comment.id)">
        {{ replyTo === comment.id ? "Cancel reply" : "Reply" }}
      </button>

      <div v-if="replyTo === comment.id" class="reply-form">
        <CommentForm :parent-id="comment.id" @created="handleCreated" />
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

    <Lightbox
      v-model="lightboxVisible"
      :src="lightboxSrc"
      alt="Attachment preview"
      type="image"
    />
  </div>
</template>

<script>
import CommentForm from "./CommentForm.vue";
import Lightbox from "./Lightbox.vue";
import { BACKEND_URL } from "../api";

export default {
  name: "CommentTree",
  components: {
    CommentForm,
    Lightbox,
    CommentTree: null, // will be set in created()
  },
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
      lightboxVisible: false,
      lightboxSrc: "",
    };
  },
  created() {
    // enable recursive component usage
    this.$options.components.CommentTree = this.$options;
  },
  methods: {
    formatDate(value) {
      if (!value) return "";
      return new Date(value).toLocaleString();
    },
    toggleReply(id) {
      this.replyTo = this.replyTo === id ? null : id;
    },
    handleCreated() {
      this.replyTo = null;
      this.$emit("changed");
    },
    isImage(attachment) {
      const path = (attachment.file || "").toLowerCase();
      return [".jpg", ".jpeg", ".png", ".gif"].some((ext) =>
        path.endsWith(ext)
      );
    },
    openLightbox(url) {
      this.lightboxSrc = url;
      this.lightboxVisible = true;
    },
  },
};
</script>

<style scoped>
.comment-item {
  border: 1px solid #e0e0e0;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
  border-radius: 6px;
  background-color: #ffffff;
}

.comment-header {
  display: flex;
  gap: 0.5rem;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.email {
  color: #666666;
}

.date {
  margin-left: auto;
  font-size: 0.8rem;
  color: #999999;
}

.comment-text {
  margin: 0.25rem 0 0.5rem;
}

.attachments {
  margin-bottom: 0.5rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.attachment-item a {
  font-size: 0.85rem;
}

.attachment-thumb {
  width: 80px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.attachment-thumb:hover {
  transform: scale(1.05);
}

.reply-btn {
  font-size: 0.85rem;
  padding: 0.25rem 0.5rem;
  margin-bottom: 0.5rem;
}

.children {
  margin-left: 1.5rem;
  padding-left: 0.75rem;
  border-left: 2px solid #f0f0f0;
}
</style>
