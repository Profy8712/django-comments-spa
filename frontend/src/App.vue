<template>
  <div class="app">
    <header class="top">
      <div class="brand">
        <div class="title">Comments SPA</div>
      </div>

      <button
        class="theme-toggle"
        type="button"
        @click="toggleTheme"
        :aria-label="themeAria"
      >
        <span class="theme-ico" aria-hidden="true">{{ themeIcon }}</span>
        <span class="theme-text">{{ themeLabel }}</span>
      </button>
    </header>

    <AuthBar :me="me" @auth-changed="handleAuthChanged" />

    <section class="section">
      <h2>New comment</h2>
      <CommentForm :me="me" :reset-key="formResetKey" @created="handleCreated" />
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
        <!-- TABLE: flat list (all comments including replies) -->
        <table v-if="flatComments.length" class="comments-table">
          <thead>
            <tr>
              <th>User Name</th>
              <th>Email</th>
              <th>Created at</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="comment in flatComments"
              :key="comment.id"
              class="row-clickable"
              @click="scrollToComment(comment.id)"
              title="Scroll to comment"
            >
              <td>{{ comment.user_name }}</td>
              <td>{{ comment.email }}</td>
              <td class="nowrap">{{ formatDate(comment.created_at) }}</td>
            </tr>
          </tbody>
        </table>

        <!-- CARDS: tree list (root + nested children) -->
        <CommentTree
          v-if="treeComments.length"
          :comments="treeComments"
          :isAdmin="isAdmin"
          :me="me"
          :reset-key="formResetKey"
          :depth="0"
          @changed="handleCreated"
        />

        <p v-else class="muted">No comments yet.</p>

        <div v-if="paginationEnabled" class="pagination">
          <button
            class="btn-outline"
            :disabled="!comments || !comments.previous"
            @click="changePage(-1)"
          >
            Prev
          </button>

          <span class="muted">Page {{ page }}</span>

          <button
            class="btn-outline"
            :disabled="!comments || !comments.next"
            @click="changePage(1)"
          >
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
import { fetchMe } from "./api/accounts";

const THEME_KEY = "theme";
const THEMES = { DARK: "dark", LIGHT: "light" };

function safeGetTheme() {
  try {
    const t = localStorage.getItem(THEME_KEY);
    return t === THEMES.LIGHT ? THEMES.LIGHT : THEMES.DARK;
  } catch (_) {
    return THEMES.DARK;
  }
}

function applyThemeToDom(theme) {
  document.documentElement.setAttribute("data-theme", theme);
}

function safeSaveTheme(theme) {
  try {
    localStorage.setItem(THEME_KEY, theme);
  } catch (_) {}
}

/**
 * Build nested tree from flat list.
 * Supports common parent field variants:
 * - parent_id
 * - parentId
 * - parent (number) OR parent (object with id)
 */

export default {
  name: "App",
  components: { AuthBar, CommentForm, CommentTree },

  data() {
    return {
      lastScrollToId: null,
      theme: THEMES.DARK,

      me: null,
      isAdmin: false,

      comments: null,
      page: 1,
      ordering: "-created_at",
      loading: false,

      ws: null,

      // forces CommentForm reset on login/logout
      formResetKey: 0,

      _highlightTimer: null,
    };
  },

  computed: {
    paginationEnabled() {
      return (
        this.comments &&
        (this.comments.next !== null || this.comments.previous !== null)
      );
    },

    // FLAT: raw list from API (table)
    flatComments() {
      if (!this.comments) return [];
      return this.comments.results || this.comments || [];
    },

    // TREE: only roots + nested children (cards)
    treeComments() {
      return this.flatComments;
    },

    themeIcon() {
      return this.theme === THEMES.DARK ? "🌙" : "☀️";
    },
    themeLabel() {
      return this.theme === THEMES.DARK ? "Dark" : "Light";
    },
    themeAria() {
      return this.theme === THEMES.DARK
        ? "Switch to light theme"
        : "Switch to dark theme";
    },
  },


  methods: {
    scrollToComment(id) {
      if (!id) return;
      requestAnimationFrame(() => {
        const el = document.getElementById(`c-${id}`) || document.querySelector(`[data-comment-id="${id}"]`);
        if (!el) return;
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        window.location.hash = `c-${id}`;
        const card = el.closest(".comment-item") || el; card.classList.add("flash-highlight");
        setTimeout(() => card.classList.remove("flash-highlight"), 1600);
      });
    },

    setTheme(theme) {
      this.theme = theme === THEMES.LIGHT ? THEMES.LIGHT : THEMES.DARK;
      applyThemeToDom(this.theme);
      safeSaveTheme(this.theme);
    },
    toggleTheme() {
      this.setTheme(this.theme === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK);
    },
    initTheme() {
      this.setTheme(safeGetTheme());
    },

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

    // called after create from CommentForm / CommentTree
    async handleCreated(payload) {
      // prefer created comment id (reply or root), fallback to parent
      this.lastScrollToId =
        payload?.id ||
        payload?.commentId ||
        payload?.parentId ||
        payload?.parent_id ||
        null;

      this.page = 1;
      await this.loadComments();

      if (!this.lastScrollToId) return;

      this.$nextTick(() => {
        const el = document.getElementById(`comment-${this.lastScrollToId}`);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
        this.lastScrollToId = null;
      });
    },

    handleAuthChanged() {
      this.formResetKey += 1;
      this.loadComments();
      this.loadMe();
    },

    async loadMe() {
        try {
          const token = localStorage.getItem("access");
          if (!token || !token.trim()) {
            this.me = null;
            this.isAdmin = false;
            return;
          }

          this.me = await fetchMe();
          this.isAdmin = !!(this.me && (this.me.is_staff || this.me.is_superuser));
        } catch (_) {
          this.me = null;
          this.isAdmin = false;
        }
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
    const hash = String(window.location.hash || "");
    const m = hash.match(/^#c-(\d+)$/);
    if (m) {
      const id = Number(m[1]);
      if (Number.isFinite(id)) {
        setTimeout(() => this.scrollToComment(id), 0);
      }
    }

    this.initTheme();
    await this.loadComments();
    await this.loadMe();
    this.setupWebSocket();
  },

  beforeUnmount() {
    if (this.ws) this.ws.close();
    if (this._highlightTimer) clearTimeout(this._highlightTimer);
  },
};
</script>

<style>
/* оставляю твой CSS как был, без ломания */
.app {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 22px 16px 40px;
}

.top {
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.brand .title {
  font-size: 28px;
  font-weight: 900;
  letter-spacing: 0.2px;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-weight: 900;
  cursor: pointer;
  user-select: none;
}
.theme-toggle:hover {
  border-color: var(--border-strong);
}

.theme-ico {
  font-size: 14px;
  line-height: 1;
}
.theme-text {
  font-size: 13px;
  letter-spacing: 0.2px;
}

.section {
  margin-top: 14px;
  padding: 14px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.22);
}
html[data-theme="light"] .section {
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.1);
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
  background: var(--surface);
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
  background: var(--surface-3);
  border: 1px solid var(--border);
  border-radius: 14px;
  margin-bottom: 12px;
}

.comments-table th,
.comments-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  font-size: 13px;
}

html:not([data-theme="light"]) .comments-table th,
html:not([data-theme="light"]) .comments-table td {
  border-bottom: 1px solid rgba(34, 48, 74, 0.7);
}

.comments-table thead th {
  background: rgba(96, 165, 250, 0.1);
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
  background: rgba(96, 165, 250, 0.1);
  color: var(--text);
  border-radius: 12px;
  padding: 9px 12px;
  cursor: pointer;
  font-weight: 800;
}
.btn-outline:hover {
  background: rgba(96, 165, 250, 0.16);
}

html[data-theme="light"] .btn-outline {
  background: #ffffff;
  border-color: rgba(37, 99, 235, 0.35);
}
html[data-theme="light"] .btn-outline:hover {
  background: #f1f5ff;
}

.pagination {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.row-clickable {
  cursor: pointer;
}
.row-clickable:hover td {
  background: rgba(96, 165, 250, 0.08);
}
html[data-theme="light"] .row-clickable:hover td {
  background: rgba(37, 99, 235, 0.06);
}

.comment-highlight {
  outline: 2px solid rgba(96, 165, 250, 0.75);
  background: rgba(96, 165, 250, 0.1) !important;
}
html[data-theme="light"] .comment-highlight {
  outline: 2px solid rgba(37, 99, 235, 0.55);
  background: rgba(37, 99, 235, 0.08) !important;
}
</style>
