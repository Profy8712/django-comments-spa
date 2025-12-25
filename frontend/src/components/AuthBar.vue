<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-head">
        <div class="auth-title">Auth</div>

        <div class="auth-status" :class="{ on: authed }">
          <span class="dot" />
          <span>{{ authed ? "Authorized" : "Anonymous" }}</span>
          <span v-if="me && (me.is_staff || me.is_superuser)" class="admin-badge">ADMIN</span>
        </div>
      </div>

      <div class="auth-form">
        <label class="lbl">Username</label>
        <input
          class="inp"
          v-model.trim="username"
          placeholder=""
          autocomplete="off"
          autocapitalize="none"
          spellcheck="false"
          inputmode="text"
          :disabled="busy || authed"
          @keydown.enter.prevent="onLogin"
        />

        <label class="lbl">Password</label>
        <input
          class="inp"
          v-model="password"
          type="password"
          placeholder=""
          autocomplete="off"
          spellcheck="false"
          :disabled="busy || authed"
          @keydown.enter.prevent="onLogin"
        />

        <div class="row">
          <button class="btn primary" :disabled="busy || authed" @click="onLogin">
            {{ busy ? "Logging in..." : "Login" }}
          </button>

          <button class="btn danger" :disabled="!authed" @click="onLogout">
            Logout
          </button>

          <button class="btn ghost" type="button" :disabled="!authed" @click="copyBearer">
            Copy Bearer
          </button>
        </div>

        <div v-if="error" class="error">{{ error }}</div>
      </div>

      <div class="muted-note">
        Tokens are stored in <code>localStorage</code>. UI updates via
        <code>auth-changed</code> event.
      </div>
    </div>
  </div>
</template>

<script>
import { isAuthed, login, logout, getAccessToken } from "../api/auth";

export default {
  name: "AuthBar",
  props: { me: { type: Object, default: null } },
  emits: ["auth-changed"],

  data() {
    return {
      authed: isAuthed(),
      username: "",
      password: "",
      busy: false,
      error: "",
    };
  },

  mounted() {
    this._onAuthChangedBound = () => this.sync();
    window.addEventListener("auth-changed", this._onAuthChangedBound);
    this.sync();
  },

  beforeUnmount() {
    window.removeEventListener("auth-changed", this._onAuthChangedBound);
  },

  methods: {
    sync() {
      this.authed = isAuthed();
      this.error = "";
      this.busy = false;

      // IMPORTANT: strict logout UX => clear BOTH fields when anonymous
      if (!this.authed) {
        this.username = "";
        this.password = "";
      }
    },

    async onLogin() {
      this.error = "";
      if (this.authed) return;

      if (!this.username || !this.password) {
        this.error = "Enter username and password.";
        return;
      }

      this.busy = true;
      try {
        await login(this.username, this.password);

        // after successful login: clear password (safe), keep username (optional)
        this.password = "";

        this.$emit("auth-changed");
      } catch (e) {
        this.error = e?.message || "Login failed.";
      } finally {
        this.busy = false;
      }
    },

    onLogout() {
      if (!this.authed) return;

      logout();

      // clear fields immediately (no waiting for event)
      this.username = "";
      this.password = "";
      this.error = "";
      this.busy = false;

      this.$emit("auth-changed");
    },

    async copyBearer() {
      const t = getAccessToken();
      if (!t) return;

      const text = `Bearer ${t}`;
      try {
        await navigator.clipboard.writeText(text);
      } catch (_) {
        const ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
      }
    },
  },
};
</script>

<style scoped>
.auth-wrap {
  margin: 18px 0;
}

/* IMPORTANT: no opacity on wrappers (it makes "fog") */
.auth-card {
  border: 1px solid var(--border);
  background: var(--surface-2);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 10px 26px rgba(0,0,0,0.18);
}

.auth-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.auth-title {
  font-weight: 900;
  letter-spacing: 0.2px;
}

.auth-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
}

.auth-status .dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.35);
}

html[data-theme="light"] .auth-status .dot {
  background: rgba(15, 23, 42, 0.28);
}

.auth-status.on .dot {
  background: var(--success);
}

.auth-form {
  display: grid;
  gap: 8px;
}

.lbl {
  font-size: 12px;
  font-weight: 800;
  color: var(--text);
}

.inp {
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--input-bg);
  color: inherit;
  outline: none;
}

.inp:focus {
  border-color: var(--border-strong);
}

.row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.btn {
  padding: 10px 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: inherit;
  font-weight: 900;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn.primary {
  background: rgba(90, 150, 255, 0.22);
  border-color: rgba(90, 150, 255, 0.35);
}
html[data-theme="light"] .btn.primary {
  background: rgba(37, 99, 235, 0.10);
  border-color: rgba(37, 99, 235, 0.35);
}

.btn.danger {
  background: rgba(255, 90, 120, 0.20);
  border-color: rgba(255, 90, 120, 0.30);
}
html[data-theme="light"] .btn.danger {
  background: rgba(225, 29, 72, 0.08);
  border-color: rgba(225, 29, 72, 0.30);
}

.btn.ghost {
  background: transparent;
}

.error {
  margin-top: 6px;
  font-size: 13px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 90, 120, 0.35);
  background: rgba(255, 90, 120, 0.10);
}

.muted-note {
  margin-top: 10px;
  font-size: 13px;
  color: var(--muted);
}

.admin-badge {
  margin-left: 8px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.4px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.45);
  color: #ef4444;
}
</style>
