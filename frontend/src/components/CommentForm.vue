<template>
  <form class="comment-form" @submit.prevent="onSubmit">
    <div class="grid2">
      <div class="form-group">
        <label class="form-label">User Name *</label>
        <input
          class="form-input"
          v-model.trim="form.user_name"
          type="text"
          :disabled="submitting"
          placeholder=""
        />
        <p v-if="errors.user_name" class="error-text">{{ errors.user_name }}</p>
      </div>

      <div class="form-group">
        <label class="form-label">Email *</label>
        <input
          class="form-input"
          v-model.trim="form.email"
          type="email"
          :disabled="submitting"
          placeholder=""
        />
        <p v-if="errors.email" class="error-text">{{ errors.email }}</p>
      </div>
    </div>

    <div class="form-group">
      <label class="form-label">Homepage</label>
      <input
        class="form-input"
        v-model.trim="form.homepage"
        type="url"
        :disabled="submitting"
        placeholder=""
      />
      <p v-if="errors.homepage" class="error-text">{{ errors.homepage }}</p>
    </div>

    <div class="form-group">
      <label class="form-label">Text *</label>

      <div class="toolbar">
        <button class="toolbar-btn" type="button" @click="insertTag('i')" :disabled="submitting">[i]</button>
        <button class="toolbar-btn" type="button" @click="insertTag('strong')" :disabled="submitting">[strong]</button>
        <button class="toolbar-btn" type="button" @click="insertTag('code')" :disabled="submitting">[code]</button>
        <button class="toolbar-btn" type="button" @click="insertTag('a')" :disabled="submitting">[a]</button>
      </div>

      <textarea
        ref="textRef"
        class="form-textarea"
        v-model="form.text"
        rows="6"
        :disabled="submitting"
        placeholder="Write your comment..."
      />
      <p v-if="errors.text" class="error-text">{{ errors.text }}</p>
    </div>

    <div class="form-group">
      <label class="form-label">Attachments</label>

      <input
        ref="fileInput"
        class="form-input"
        type="file"
        multiple
        accept=".jpg,.jpeg,.png,.gif,.webp,.txt"
        @change="onFilesSelected"
        :disabled="submitting || !hasJwt"
      />

      <p v-if="!hasJwt" class="hint-lock">
        🔒 Login to attach files.
      </p>

      <div v-if="hasJwt" class="hint-text">
        Allowed: images (JPG/PNG/GIF/WEBP) and TXT (≤100 KB).
      </div>

      <div v-if="hasJwt && selectedFiles.length" class="files-list">
        <div v-for="(f, idx) in selectedFiles" :key="idx" class="file-item">
          <span class="file-name">{{ f.file.name }}</span>
          <span class="file-size">({{ formatBytes(f.file.size) }})</span>
          <span v-if="f.error" class="file-error">{{ f.error }}</span>
          <button class="file-remove" type="button" @click="removeFile(idx)" :disabled="submitting">✕</button>
        </div>
      </div>

      <p v-if="errors.attachments" class="error-text">{{ errors.attachments }}</p>
    </div>

    <div v-if="!hasJwt" class="form-group">
      <label class="form-label">CAPTCHA *</label>

      <div class="captcha-row">
        <img v-if="captcha.image" class="captcha-image" :src="captcha.image" alt="CAPTCHA" />

        <button
          class="captcha-reload"
          type="button"
          @click="loadCaptcha"
          :disabled="submitting || captchaLoading"
          title="Reload CAPTCHA"
        >
          ⟳
        </button>

        <input
          class="form-input captcha-input"
          v-model.trim="form.captcha_value"
          type="text"
          autocomplete="off"
          :disabled="submitting"
          placeholder="Enter text from image"
        />
      </div>

      <p v-if="errors.captcha_value" class="error-text">{{ errors.captcha_value }}</p>
    </div>

    <div class="form-actions">
      <button class="btn" type="submit" :disabled="submitting">
        {{ submitting ? "Sending..." : "Send comment" }}
      </button>
    </div>

    <p v-if="errors.non_field" class="error-text">{{ errors.non_field }}</p>
  </form>
</template>

<script>
import { apiGet, getAccessToken, buildUrl } from "../api/index";
import { createComment } from "../api/comments";
import { uploadAttachment } from "../api/attachments";

export default {
  name: "CommentForm",
  emits: ["created"],
  props: {
    parent_id: { type: [Number, String, null], default: null },
  },

  data() {
    return {
      submitting: false,
      captchaLoading: false,
      hasJwt: false,
      captcha: { key: "", image: "" },
      selectedFiles: [],
      errors: {},

      form: {
        user_name: "",
        email: "",
        homepage: "",
        text: "",
        captcha_key: "",
        captcha_value: "",
      },
    };
  },

  mounted() {
    this._onAuthChangedBound = () => this.onAuthChanged();
    this.syncAuth();

    if (!this.hasJwt) this.loadCaptcha();
    window.addEventListener("auth-changed", this._onAuthChangedBound);
  },

  beforeUnmount() {
    window.removeEventListener("auth-changed", this._onAuthChangedBound);
  },

  methods: {
    syncAuth() {
      this.hasJwt = !!getAccessToken();
      if (this.hasJwt) {
        this.form.captcha_key = "";
        this.form.captcha_value = "";
      }
    },

    onAuthChanged() {
      const was = this.hasJwt;
      this.syncAuth();

      if (!was && this.hasJwt) {
        this.errors = {};
        this.clearFiles();
      }

      if (was && !this.hasJwt) {
        this.clearFiles();
        this.loadCaptcha();
      }
    },

    clearFiles() {
      this.selectedFiles = [];
      const inp = this.$refs.fileInput;
      if (inp) inp.value = "";
    },

    async loadCaptcha() {
      this.captchaLoading = true;
      try {
        const data = await apiGet("/api/comments/captcha/");
        const key = data?.key || "";
        const img = data?.image || data?.image_url || "";

        this.captcha.key = key;

        // IMPORTANT: buildUrl so it works with VITE_API_URL and with proxy
        this.captcha.image = buildUrl(img);

        this.form.captcha_key = key;
        this.form.captcha_value = "";
      } catch (e) {
        this.errors.captcha_value = "Failed to load CAPTCHA.";
      } finally {
        this.captchaLoading = false;
      }
    },

    insertTag(tag) {
      const el = this.$refs.textRef;
      if (!el) return;

      const open = `[${tag}]`;
      const close = `[/${tag}]`;

      const start = el.selectionStart ?? 0;
      const end = el.selectionEnd ?? 0;

      const before = this.form.text.slice(0, start);
      const selected = this.form.text.slice(start, end);
      const after = this.form.text.slice(end);

      this.form.text = `${before}${open}${selected}${close}${after}`;

      this.$nextTick(() => {
        el.focus();
        const pos = start + open.length + selected.length + close.length;
        el.setSelectionRange(pos, pos);
      });
    },

    onFilesSelected(e) {
      this.syncAuth();
      if (!this.hasJwt) {
        this.clearFiles();
        return;
      }

      const files = Array.from(e?.target?.files || []);
      this.selectedFiles = files.map((file) => ({
        file,
        error: this.validateFile(file),
      }));
    },

    validateFile(file) {
      const name = (file.name || "").toLowerCase();
      const isTxt = name.endsWith(".txt");
      const isImg =
        name.endsWith(".jpg") ||
        name.endsWith(".jpeg") ||
        name.endsWith(".png") ||
        name.endsWith(".gif") ||
        name.endsWith(".webp");

      if (!isTxt && !isImg) return "Only images (JPG/PNG/GIF/WEBP) or TXT are allowed.";
      if (isTxt && file.size > 100 * 1024) return "TXT must be <= 100 KB.";
      return null;
    },

    removeFile(idx) {
      this.selectedFiles.splice(idx, 1);
    },

    formatBytes(bytes) {
      if (!bytes) return "0 B";
      const k = 1024;
      const sizes = ["B", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      const val = bytes / Math.pow(k, i);
      return `${val.toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`;
    },

    mapApiErrors(err) {
      const payload = err?.payload;
      if (payload && typeof payload === "object") {
        const out = {};
        for (const [k, v] of Object.entries(payload)) {
          out[k] = Array.isArray(v) ? v.join(" ") : String(v);
        }
        return out;
      }
      return { non_field: "Request failed." };
    },

    async onSubmit() {
      this.errors = {};
      this.syncAuth();

      // validate
      if (!this.form.text) this.errors.text = "Text is required.";
      if (!this.form.user_name) this.errors.user_name = "User Name is required.";
      if (!this.form.email) this.errors.email = "Email is required.";

      if (!this.hasJwt) {
        if (!this.form.captcha_key || !this.form.captcha_value) {
          this.errors.captcha_value = "CAPTCHA is required.";
        }
      }

      if (Object.keys(this.errors).length) return;

      this.submitting = true;

      try {
        const payload = {
          user_name: this.form.user_name,
          email: this.form.email,
          homepage: this.form.homepage || null,
          text: this.form.text,
        };

        if (this.parent_id) payload.parent = this.parent_id;

        if (!this.hasJwt) {
          payload.captcha_key = this.form.captcha_key;
          payload.captcha_value = this.form.captcha_value;
        }

        // 1) create comment
        const created = await createComment(payload);

        // 2) upload attachments (auth only)
        if (this.hasJwt && this.selectedFiles.length) {
          const okFiles = this.selectedFiles.filter((f) => !f.error).map((f) => f.file);
          for (const file of okFiles) {
            await uploadAttachment(created.id, file);
          }
        }

        // reset
        this.form.text = "";
        this.form.homepage = "";
        this.clearFiles();

        if (!this.hasJwt) await this.loadCaptcha();

        // refresh list AFTER uploads finished
        this.$emit("created", created);

        // extra refresh tick (small race guard)
        setTimeout(() => {
          this.$emit("created", created);
        }, 250);
      } catch (err) {
        this.errors = this.mapApiErrors(err);
        if (!this.hasJwt && (this.errors.captcha_value || this.errors.captcha_key)) {
          await this.loadCaptcha();
        }
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 14px;

  width: 100%;
  margin: 0;

  background: rgba(17, 28, 51, 0.70);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 10px 26px rgba(0,0,0,0.18);
}

.grid2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
@media (max-width: 760px) {
  .grid2 {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-weight: 900;
  color: var(--text);
}

.form-input,
.form-textarea {
  background: rgba(15, 23, 42, 0.85);
  color: var(--text);
  border: 1px solid rgba(34, 48, 74, 0.85);
  border-radius: 14px;
  padding: 10px 12px;
  font-size: 14px;
  outline: none;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: rgba(148, 163, 184, 0.9);
  opacity: 1;
}

.form-input:focus,
.form-textarea:focus {
  border-color: rgba(96, 165, 250, 0.55);
  box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.16);
}

.form-textarea {
  resize: vertical;
}

.error-text {
  color: var(--danger, #ff5a78);
  font-size: 13px;
}

.hint-text {
  color: var(--muted);
  font-size: 13px;
}

.hint-lock {
  color: var(--muted);
  font-size: 13px;
  opacity: 0.95;
}

/* Toolbar */
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.toolbar-btn {
  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.10);
  border-radius: 12px;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 900;
  color: var(--text);
}
.toolbar-btn:hover {
  background: rgba(96, 165, 250, 0.16);
}

/* Files */
.files-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 6px;
}

.file-item {
  display: flex;
  gap: 10px;
  align-items: center;
  border: 1px solid rgba(34, 48, 74, 0.85);
  border-radius: 14px;
  padding: 8px 10px;
  background: rgba(15, 23, 42, 0.65);
}

.file-name {
  font-weight: 900;
  color: var(--text);
}

.file-size {
  color: var(--muted);
  font-size: 13px;
}

.file-error {
  color: var(--danger, #ff5a78);
  font-size: 13px;
  margin-left: auto;
}

.file-remove {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  color: var(--text);
  opacity: 0.9;
}
.file-remove:hover {
  opacity: 1;
}

/* Captcha */
.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.captcha-image {
  height: 48px;
  width: auto;
  border-radius: 12px;
  border: 1px solid rgba(34, 48, 74, 0.85);
  background: rgba(15, 23, 42, 0.85);
}

.captcha-reload {
  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.10);
  border-radius: 12px;
  padding: 8px 10px;
  cursor: pointer;
  font-weight: 900;
  color: var(--text);
}
.captcha-reload:hover {
  background: rgba(96, 165, 250, 0.16);
}

.captcha-input {
  flex: 1;
  min-width: 220px;
}

/* Submit */
.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 4px;
}

.btn {
  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.16);
  color: var(--text);
  border-radius: 16px;
  padding: 12px 18px;
  cursor: pointer;
  font-weight: 900;
  min-width: 190px;
}

.btn:hover {
  background: rgba(96, 165, 250, 0.20);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
