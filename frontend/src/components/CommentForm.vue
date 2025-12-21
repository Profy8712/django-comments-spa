<!-- frontend/src/components/CommentForm.vue -->
<template>
  <form class="comment-form" @submit.prevent="onSubmit">
    <div class="form-group">
      <label class="form-label">User Name *</label>
      <input
        class="form-input"
        v-model.trim="form.user_name"
        type="text"
        placeholder="Your name"
        :disabled="submitting"
      />
      <p v-if="errors.user_name" class="error-text">{{ errors.user_name }}</p>
    </div>

    <div class="form-group">
      <label class="form-label">Email *</label>
      <input
        class="form-input"
        v-model.trim="form.email"
        type="email"
        placeholder="your@email.com"
        :disabled="submitting"
      />
      <p v-if="errors.email" class="error-text">{{ errors.email }}</p>
    </div>

    <div class="form-group">
      <label class="form-label">Homepage</label>
      <input
        class="form-input"
        v-model.trim="form.homepage"
        type="url"
        placeholder="https://example.com"
        :disabled="submitting"
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
        placeholder="Write your comment..."
        :disabled="submitting"
      />
      <p v-if="errors.text" class="error-text">{{ errors.text }}</p>
    </div>

    <!-- Attachments -->
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

      <p v-if="!hasJwt" class="error-text">
        Attachments are available only for logged-in users.
      </p>

      <!-- show selected files only for JWT users -->
      <div v-if="hasJwt && selectedFiles.length" class="files-list">
        <div v-for="(f, idx) in selectedFiles" :key="idx" class="file-item">
          <span class="file-name">{{ f.file.name }}</span>
          <span class="file-size">({{ formatBytes(f.file.size) }})</span>

          <span v-if="f.error" class="file-error">{{ f.error }}</span>

          <button class="file-remove" type="button" @click="removeFile(idx)" :disabled="submitting">
            ✕
          </button>
        </div>
      </div>

      <p v-if="errors.attachments" class="error-text">{{ errors.attachments }}</p>
    </div>

    <!-- CAPTCHA -->
    <div v-if="!hasJwt" class="form-group">
      <label class="form-label">CAPTCHA *</label>

      <div class="captcha-row">
        <div class="captcha-image-wrapper">
          <img v-if="captcha.image" class="captcha-image" :src="captcha.image" alt="CAPTCHA" />
        </div>

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
          placeholder="Enter text from image"
          :disabled="submitting"
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
import { apiGet, getAccessToken } from "../api/index";
import { createComment } from "../api/comments";
import { uploadAttachment } from "../api/attachments";

export default {
  name: "CommentForm",
  emits: ["created"],

  props: {
    parent_id: {
      type: [Number, String, null],
      default: null,
    },
  },

  data() {
    return {
      submitting: false,
      captchaLoading: false,

      // reactive auth state
      hasJwt: false,

      captcha: { key: "", image: "" },

      form: {
        user_name: "",
        email: "",
        homepage: "",
        text: "",
        captcha_key: "",
        captcha_value: "",
      },

      // [{ file: File, error: string|null }]
      selectedFiles: [],

      errors: {},
    };
  },

  mounted() {
    // bind once so removeEventListener works
    this._onStorageBound = (e) => this.onStorage(e);
    this._onAuthChangedBound = () => this.onAuthChanged();

    this.syncAuth();

    if (!this.hasJwt) {
      this.loadCaptcha();
    }

    // 1) works for other tabs/windows (not same tab)
    window.addEventListener("storage", this._onStorageBound);

    // 2) works for same tab: dispatch this event after saving tokens
    window.addEventListener("auth-changed", this._onAuthChangedBound);
  },

  beforeUnmount() {
    window.removeEventListener("storage", this._onStorageBound);
    window.removeEventListener("auth-changed", this._onAuthChangedBound);
  },

  methods: {
    onStorage(e) {
      // Fires ONLY when localStorage changes in ANOTHER tab
      if (e && (e.key === "access" || e.key === "refresh")) {
        this.syncAuth();
      }
    },

    onAuthChanged() {
      // Fires in SAME tab when we dispatch custom event
      const wasAuthed = this.hasJwt;
      this.syncAuth();

      // If we just became authed, hide captcha errors, etc.
      if (!wasAuthed && this.hasJwt) {
        this.errors.captcha_value = "";
      }

      // If we just became anonymous, ensure captcha exists
      if (wasAuthed && !this.hasJwt) {
        this.loadCaptcha();
      }
    },

    syncAuth() {
      this.hasJwt = !!getAccessToken();

      if (!this.hasJwt) {
        // anonymous -> captcha required, files forbidden
        this.clearFiles();
        // keep captcha fields (will be filled by loadCaptcha)
      } else {
        // JWT -> captcha not needed
        this.form.captcha_key = "";
        this.form.captcha_value = "";
      }
    },

    clearFiles() {
      this.selectedFiles = [];
      const inp = this.$refs.fileInput;
      if (inp) inp.value = "";
    },

    async loadCaptcha() {
      this.captchaLoading = true;
      this.errors.captcha_value = "";

      try {
        // endpoint in your backend: GET /api/comments/captcha/
        const data = await apiGet("/api/comments/captcha/");
        const key = data?.key || "";
        // your backend may return "image" or "image_url" - handle both
        const img = data?.image || data?.image_url || "";

        this.captcha.key = key;
        this.captcha.image = this.resolveUrl(img);

        this.form.captcha_key = key;
        this.form.captcha_value = "";
      } catch (e) {
        this.errors.captcha_value = "Failed to load CAPTCHA.";
      } finally {
        this.captchaLoading = false;
      }
    },

    resolveUrl(pathOrUrl) {
      if (!pathOrUrl) return "";
      if (pathOrUrl.startsWith("http://") || pathOrUrl.startsWith("https://")) return pathOrUrl;
      const p = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
      return `${window.location.protocol}//${window.location.host}${p}`;
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
        const cursorPos = start + open.length + selected.length + close.length;
        el.setSelectionRange(cursorPos, cursorPos);
      });
    },

    onFilesSelected(e) {
      // HARD GUARD: anonymous must never accept files
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

      // HARD GUARD: anonymous must never upload files
      if (!this.hasJwt) {
        this.clearFiles();
      }

      // simple validation
      if (!this.form.user_name) this.errors.user_name = "User Name is required.";
      if (!this.form.email) this.errors.email = "Email is required.";
      if (!this.form.text) this.errors.text = "Text is required.";

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

        if (this.parent_id) {
          payload.parent = this.parent_id;
        }

        if (!this.hasJwt) {
          payload.captcha_key = this.form.captcha_key;
          payload.captcha_value = this.form.captcha_value;
        }

        const created = await createComment(payload);

        // Upload attachments ONLY for JWT users
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

        if (!this.hasJwt) {
          await this.loadCaptcha();
        }

        this.$emit("created", created);
      } catch (err) {
        this.errors = this.mapApiErrors(err);

        // refresh captcha after captcha-related errors
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
  max-width: 720px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-weight: 600;
}

.form-input,
.form-textarea {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
  outline: none;
}

.form-textarea {
  resize: vertical;
}

.error-text {
  color: #e74c3c;
  font-size: 13px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.toolbar-btn {
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 13px;
}

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
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 8px 10px;
}

.file-name {
  font-weight: 600;
}

.file-size {
  color: #777;
  font-size: 13px;
}

.file-error {
  color: #e74c3c;
  font-size: 13px;
  margin-left: auto;
}

.file-remove {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
}

.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.captcha-image {
  display: block;
  height: 48px;
  width: auto;
}

.captcha-reload {
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 8px;
  padding: 8px;
  cursor: pointer;
}

.captcha-input {
  flex: 1;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
}

.btn {
  background: #111;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 10px 16px;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
