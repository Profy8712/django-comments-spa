<template>
  <div class="app">
    <h1>Comments SPA</h1>

    <section class="section">
      <h2>New comment</h2>
      <CommentForm @created="handleCreated" />
    </section>

    <section class="section">
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

      <div v-if="loading" class="loading">
        Loading comments...
      </div>

      <div v-else>
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
              <td>{{ formatDate(comment.created_at) }}</td>
            </tr>
          </tbody>
        </table>

        <CommentTree
          v-if="currentComments.length"
          :comments="currentComments"
          @changed="loadComments"
        />

        <p v-else>No comments yet.</p>

        <div v-if="paginationEnabled" class="pagination">
          <button :disabled="!comments.previous" @click="changePage(-1)">
            Prev
          </button>
          <span>Page {{ page }}</span>
          <button :disabled="!comments.next" @click="changePage(1)">
            Next
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import CommentForm from "./components/CommentForm.vue";
import CommentTree from "./components/CommentTree.vue";
import { fetchComments } from "./api/comments";

export default {
  name: "App",
  components: {
    CommentForm,
    CommentTree,
  },
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
      return (
        this.comments &&
        (this.comments.next !== null || this.comments.previous !== null)
      );
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
        const data = await fetchComments(this.page, this.ordering);
        this.comments = data;
      } catch (error) {
        console.error("Failed to fetch comments:", error);
      } finally {
        this.loading = false;
      }
    },

    async changePage(delta) {
      this.page += delta;
      if (this.page < 1) {
        this.page = 1;
      }
      await this.loadComments();
    },

    async onOrderingChange() {
      this.page = 1;
      await this.loadComments();
    },

    async handleCreated() {
      await this.loadComments();
    },

    formatDate(value) {
      if (!value) return "";
      const date = new Date(value);
      return date.toLocaleString();
    },

    setupWebSocket() {
      const protocol = window.location.protocol === "https:" ? "wss" : "ws";
      const wsUrl = `${protocol}://${window.location.host}/ws/comments/`;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log("WebSocket connected:", wsUrl);
      };

      this.ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "comment_created") {
            await this.loadComments();
          }
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      this.ws.onclose = () => {
        console.log("WebSocket disconnected");
        this.ws = null;
      };

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    },
  },
  async mounted() {
    await this.loadComments();
    this.setupWebSocket();
  },
  beforeUnmount() {
    if (this.ws) {
      this.ws.close();
    }
  },
};
</script>

<style>
.app {
  max-width: 900px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}

.section {
  margin-bottom: 1.5rem;
}

.controls {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.loading {
  font-size: 0.95rem;
  color: #555;
}

.pagination {
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.comments-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.comments-table th,
.comments-table td {
  border: 1px solid #e5e7eb;
  padding: 0.45rem 0.6rem;
  text-align: left;
}

.comments-table thead {
  background-color: #f3f4f6;
}

.comments-table th {
  font-weight: 600;
}
</style>
