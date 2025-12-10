<template>
  <div class="comment-tree">
    <div
      v-for="comment in comments"
      :key="comment.id"
      class="comment-item"
    >
      <div class="comment-header">
        <strong>{{ comment.user_name }}</strong>
        <span class="email">{{ comment.email }}</span>
        <span class="date">{{ formatDate(comment.created_at) }}</span>
      </div>

      <!-- SAFE HTML RENDER -->
      <div
        class="comment-text"
        v-html="renderSafeHtml(comment.text)"
      ></div>

      <!-- Attachments -->
      <div v-if="comment.attachments.length" class="attachments">
        <div
          v-for="file in comment.attachments"
          :key="file.id"
          class="attachment"
        >
          <template v-if="isImage(file.file)">
            <img
              :src="file.file"
              class="preview-image"
              @click="openLightbox(file.file)"
            />
          </template>

          <template v-else>
            <a :href="file.file" download>Download file</a>
          </template>
        </div>
      </div>

      <!-- Reply button -->
      <button class="reply-button" @click="startReply(comment.id)">
        Reply
      </button>

      <!-- Nested children -->
      <CommentTree
        v-if="comment.children && comment.children.length"
        :comments="comment.children"
        @changed="$emit('changed')"
      />
    </div>

    <!-- Lightbox overlay -->
    <div v-if="lightboxImage" class="lightbox-overlay" @click="closeLightbox">
      <img :src="lightboxImage" class="lightbox-image" />
    </div>
  </div>
</template>

<script>
import { renderSafeHtml } from "../helpers/render.js";

export default {
  name: "CommentTree",
  props: {
    comments: {
      type: Array,
      required: true,
    },
  },
  methods: {
    renderSafeHtml,
    formatDate(value) {
      if (!value) return "";
      return new Date(value).toLocaleString();
    },
    isImage(url) {
      return /\.(jpg|jpeg|png|gif)$/i.test(url);
    },
    openLightbox(src) {
      this.lightboxImage = src;
    },
    closeLightbox() {
      this.lightboxImage = null;
    },
    startReply(commentId) {
      this.$emit("reply", commentId);
    },
  },
  data() {
    return {
      lightboxImage: null,
    };
  },
};
</script>

<style scoped>
.comment-tree {
  margin-left: 1rem;
}

.comment-item {
  margin-bottom: 1.2rem;
  padding-left: 0.5rem;
  border-left: 2px solid #ddd;
}

.comment-header {
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
}

.email {
  color: #666;
  margin-left: 0.5rem;
}

.date {
  color: #999;
  margin-left: 0.5rem;
}

.comment-text {
  margin: 0.3rem 0 0.5rem;
  line-height: 1.4;
}

.preview-image {
  width: 120px;
  cursor: pointer;
  border-radius: 4px;
  margin-right: 0.5rem;
}

.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}

.lightbox-image {
  max-width: 90%;
  max-height: 90%;
  border-radius: 6px;
}

.reply-button {
  margin-top: 0.3rem;
  padding: 3px 7px;
  font-size: 0.8rem;
  cursor: pointer;
}
</style>
