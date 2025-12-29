<template>
  <div class="comment-tree">
    <div
      v-for="c in comments"
      :key="c.id"
      class="comment-item" :id="`c-${c.id}`" :data-comment-id="c.id"
      :class="{
        'is-child': isChild,
        'is-highlight': highlightId === c.id
      }"
    >
      <!-- Header -->
      <div class="comment-head">
        <div class="avatar">{{ avatarLetter(c) }}</div>

        <div class="meta comment-meta">
          <div class="line1">
            <span class="author comment-author">{{ c.user_name || c.username || "Anonymous" }}</span>
            <span class="muted dot">•</span>
            <span class="time muted">{{ formatDate(c.created_at || c.created || c.createdAt) }}</span>
          </div>
          <div class="line2" >
            <span class="email muted">{{ c.email }}</span>
          </div>
        </div>

        <div class="actions comment-actions">
          <button type="button" class="btn-link" @click="toggleReply(c.id)">Reply</button>

          <button
              v-if="isAdmin"
              class="btn-link btn-link-danger"
            type="button"
            @click.stop.prevent="onDelete(c.id)"
            title="Delete comment"
          >
            Delete
          </button>
        </div>
      </div>

      <!-- Body -->
      <div class="comment-body">
        <div class="comment-text">{{ c.text }}</div>

        <!-- Attachments -->
          <div v-if="c.attachments && c.attachments.length" class="attach">
          <template v-for="a in c.attachments" :key="a.id">
            <img
              v-if="isImage(a.file)"
              class="attach-img" @click.stop="openLightboxImage(a.file, filenameFromUrl(a.file))"
              :src="a.file"
              alt="attachment"
              loading="lazy"
            />
            <a
              v-else
              class="attach-item"
              :href="a.file"
              target="_blank"
              rel="noreferrer"
            >
              {{ filenameFromUrl(a.file) }}
            </a>

          </template>
        </div>
      </div>

      <!-- Reply form -->
      <div v-if="replyOpenId === c.id" class="reply-form">
        <div  class="reply-quote">
          {{ shorten(c.text) }}
        </div>

        <CommentForm
          :parent-id="c.id"
          :isAdmin="isAdmin"
          :me="me"
          :reset-key="resetKey"
          @created="onChanged"
          @cancel="toggleReply(null)"
        />
      </div>

      <!-- Children -->
      <div  class="children comment-children">
        <CommentTree
          :comments="c.children"
          :isAdmin="isAdmin"
          :me="me"
          :reset-key="resetKey"
          :is-child="true"
          @changed="onChanged"
          @delete="onDelete"
        />
      </div>
    </div>
  </div>
    <Lightbox
      v-model="lightboxOpen"
      :src="lightboxSrc"
      :alt="lightboxAlt"
      :type="lightboxType"
    />

</template>

<script>
import CommentForm from "./CommentForm.vue";
import Lightbox from "./Lightbox.vue";


export default {
  name: "CommentTree",
  components: { CommentForm, Lightbox },

  props: {
    comments: { type: Array, default: () => [] },
    isAdmin: { type: Boolean, default: false },
    me: { type: Object, default: null },
    resetKey: { type: [String, Number], default: 0 },
    isChild: { type: Boolean, default: false }
  },

  emits: ["changed", "delete"],

  data() {
    return {
      lightboxOpen: false,
      lightboxAlt: "",
      lightboxType: "image",

      replyOpenId: null,
      highlightId: null,
      _hlTimer: null
    };
  },

  beforeUnmount() {
    if (this._hlTimer) clearTimeout(this._hlTimer);
  },

  methods: {
    openLightboxImage(src, alt = "Attachment") {
      if (!src) return;
      this.lightboxSrc = String(src);
      this.lightboxType = "image";
      this.lightboxAlt = String(alt || "Attachment");
      this.lightboxOpen = true;
    },

    toggleReply(id) {
      if (id === null) {
        this.replyOpenId = null;
        return;
      }
      this.replyOpenId = this.replyOpenId === id ? null : id;
    },

    onChanged(payload) {
      this.replyOpenId = null;

      const newId =
        payload?.id ||
        payload?.comment?.id ||
        payload?.data?.id ||
        payload?.created?.id ||
        null;

      if (newId) {
        this.highlightId = newId;
        if (this._hlTimer) clearTimeout(this._hlTimer);
        this._hlTimer = setTimeout(() => {
          this.highlightId = null;
        }, 1600);
      }

      this.$emit("changed", payload);
    },

    onDelete(id) {
      this.$emit("delete", id);
    },

    avatarLetter(c) {
      const name = String(c?.user_name || c?.username || "U").trim();
      return name ? name[0].toUpperCase() : "U";
    },

    formatDate(v) {
      if (!v) return "";
      try {
        const d = new Date(v);
        return isNaN(d.getTime()) ? String(v) : d.toLocaleString();
      } catch {
        return String(v);
      }
    },

    shorten(text) {
      const s = String(text || "").trim();
      return s.length <= 140 ? s : s.slice(0, 140) + "…";
    },

    filenameFromUrl(url) {
      const s = String(url || "");
      const clean = s.split("?")[0];
      const parts = clean.split("/");
      return parts[parts.length - 1] || "file";
    },

    isImage(url) {
      const s = String(url || "").toLowerCase().split("?")[0];
      return (
        s.endsWith(".jpg") ||
        s.endsWith(".jpeg") ||
        s.endsWith(".png") ||
        s.endsWith(".gif") ||
        s.endsWith(".webp")
      );
    }
  }
};
</script>

<style scoped>
.comment-tree {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* Forum-like card */
.comment-item {
  transition: border-color 180ms ease, box-shadow 180ms ease, background-color 180ms ease;

  position: relative;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px 14px;
}

.comment-item.is-highlight {
  border-color: var(--border-strong);
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.10);
}

/* ✅ Forum header bar like screenshot #2 */
.comment-head {
  display: grid;
  grid-template-columns: 34px 1fr auto;
  gap: 12px;
  align-items: center;

  padding: 10px 12px;
  margin: -12px -14px 12px; /* stretch to edges of card */
  background: rgba(15, 23, 42, 0.03);
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px 14px 0 0;
}

html:not([data-theme="light"]) .comment-head {
  background: rgba(255, 255, 255, 0.06);
  border-bottom-color: rgba(255, 255, 255, 0.14);
}

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-weight: 900;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid var(--border);
  color: var(--text);
}

.meta { min-width: 0; }

.line1 {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.author { font-weight: 900; }
.dot { opacity: 0.7; }
.time { font-size: 0.9rem; }

.line2 { margin-top: 2px; }
.email { font-size: 0.9rem; }

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* Body */
.comment-body { padding: 0; }

.comment-text {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 1rem;
}

/* Attachments */
.attach {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: flex-start;
}

.attach-img {
  cursor: zoom-in;
  width: 140px;
  height: 105px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.04);
  display: block;
}

.attach-item {
  font-size: 0.92rem;
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  text-decoration: none;
  color: var(--text);
  background: rgba(255, 255, 255, 0.03);
}

html[data-theme="light"] .attach-item {
  background: rgba(15, 23, 42, 0.03);
}

/* Reply */
.reply-form {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.reply-quote {
  font-size: 0.95rem;
  color: var(--muted);
  padding: 8px 12px;
  border-left: 3px solid rgba(37, 99, 235, 0.45);
  border-radius: 10px;
  background: rgba(37, 99, 235, 0.04);
  margin-bottom: 10px;
  line-height: 1.45;
}

/* ✅ Children: forum quote indentation + soft child background */
.children {
  margin-top: 12px;
  padding-left: 16px;
  border-left: 3px solid rgba(148, 163, 184, 0.45);
}

.comment-item.is-child {
  margin-top: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.02);
}

html:not([data-theme="light"]) .comment-item.is-child {
  background: rgba(255, 255, 255, 0.04);
}
/* highlight when navigated via #c-<id> */

</style>
