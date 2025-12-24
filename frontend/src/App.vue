<template>
  <div class="app">
    <header class="top">
      <div class="brand">
        <div class="title">Comments SPA</div>
        <div class="subtitle">Django + Vue • JWT • WebSocket • Attachments • CAPTCHA</div>
      </div>
    </header>

    <AuthBar @auth-changed="handleAuthChanged" />

    <section class="section">
      <h2>New comment</h2>
      <CommentForm @created="handleCreated" />
    </section>

    <section class="section">
      <div class="section-head">
        <h2>Comments</h2>

        <div class="controls">
          <label>Sort by:</label>
          <select v-model="ordering" @change="onOrderingChange">
            <option value="-created_at">Newest first (LIFO)</option>
            <option value="created_at">Oldest first</option>
            <option value="user_name">User name A-Z</option>
            <option value="-user_name">User name Z-A</option>
            <option value="email">Email A-Z</option>
            <option value="-email">Email Z-A</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="loading">Loading comments...</div>

      <div v-else class="comments-wrap">
        <table v-if="currentComments.length" class="comments-table">
          <thead>
            <tr>
              <th>User Name</th>
              <th>Email</th>
              <th>Created at</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="comment in currentComments" :key="comment.id">
              <td>{{ comment.user_name }}</td>
              <td>{{ comment.email }}</td>
              <td class="nowrap">{{ formatDate(comment.created_at) }}</td>
            </tr>
          </tbody>
        </table>

        <CommentTree
          v-if="currentComments.length"
          :comments="currentComments"
          @changed="loadComments"
        />

        <p v-else class="muted">No comments yet.</p>

        <div v-if="paginationEnabled" class="pagination">
          <button class="btn-outline" :disabled="!comments.previous" @click="changePage(-1)">
            Prev
          </button>
          <span class="muted">Page {{ page }}</span>
          <button class="btn-outline" :disabled="!comments.next" @click="changePage(1)">
            Next
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import AuthBar from "./components/AuthBar.vue";
import CommentForm from "./components/CommentForm.vue";
import CommentTree from "./components/CommentTree.vue";
import { fetchComments } from "./api/comments";

export default {
  name: "App",
  components: { AuthBar, CommentForm, CommentTree },

  data() {
    return {
      comments: null,
      page: 1,
      ordering: "-created_at",
      loading: false,
      ws: null,
    };
  },

  computed: {
    paginationEnabled() {
      return this.comments && (this.comments.next !== null || this.comments.previous !== null);
    },
    currentComments() {
      if (!this.comments) return [];
      return this.comments.results || this.comments;
    },
  },

  methods: {
    async loadComments() {
      this.loading = true;
      try {
        this.comments = await fetchComments(this.page, this.ordering);
      } catch (error) {
        console.error("Failed to fetch comments:", error);
      } finally {
        this.loading = false;
      }
    },

    async changePage(delta) {
      this.page = Math.max(1, this.page + delta);
      await this.loadComments();
    },

    async onOrderingChange() {
      this.page = 1;
      await this.loadComments();
    },

    async handleCreated() {
      // One refresh is usually enough
      await this.loadComments();

      // But attachments can be attached right after upload (small race),
      // so we do a tiny extra refresh to ensure UI shows attachments immediately.
      setTimeout(() => {
        this.loadComments();
      }, 300);
    },

    handleAuthChanged() {
      // When auth changes, it’s often useful to refresh comments list (optional).
      // Keeps UI consistent with permissions.
      this.loadComments();
    },

    formatDate(value) {
      if (!value) return "";
      return new Date(value).toLocaleString();
    },

    setupWebSocket() {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const wsUrl = `${protocol}://${window.location.host}/ws/comments/`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => console.log("WebSocket connected:", wsUrl);

      this.ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "comment_created") await this.loadComments();
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
        this.ws = null;
      };

      this.ws.onerror = (error) => console.error("WebSocket error:", error);
    },
  },

  async mounted() {
    await this.loadComments();
    this.setupWebSocket();
  },

  beforeUnmount() {
    if (this.ws) this.ws.close();
  },
};
</script>

<style>
.app {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 22px 16px 40px;
}

.top {
  margin-bottom: 12px;
}
.brand .title {
  font-size: 28px;
  font-weight: 900;
  letter-spacing: 0.2px;
}
.brand .subtitle {
  margin-top: 4px;
  color: var(--muted);
  font-size: 13px;
}

.section {
  margin-top: 14px;
  padding: 14px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
}
.section h2 {
  margin: 0 0 10px;
  font-size: 18px;
}

.section-head {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.controls {
  display: flex;
  gap: 8px;
  align-items: center;
}
.controls label {
  color: var(--muted);
  font-size: 13px;
}
.controls select {
  background: var(--surface, rgba(0,0,0,0.2));
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 8px 10px;
  outline: none;
}

.comments-wrap {
  margin-top: 8px;
}
.comments-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: rgba(17, 28, 51, 0.8);
  border: 1px solid var(--border);
  border-radius: 14px;
  overflow: hidden;
  margin-bottom: 12px;
}
.comments-table th,
.comments-table td {
  padding: 10px 12px;
  border-bottom: 1px solid rgba(34, 48, 74, 0.7);
  text-align: left;
  font-size: 13px;
}
.comments-table thead th {
  background: rgba(96, 165, 250, 0.10);
  font-weight: 800;
}
.comments-table tbody tr:last-child td {
  border-bottom: none;
}
.nowrap {
  white-space: nowrap;
}

.loading {
  color: var(--muted);
  font-size: 13px;
}

.muted {
  color: var(--muted);
}

.btn-outline {
  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.10);
  color: var(--text);
  border-radius: 12px;
  padding: 9px 12px;
  cursor: pointer;
  font-weight: 800;
}
.btn-outline:hover {
  background: rgba(96, 165, 250, 0.16);
}

.pagination {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
</style>
