<template>
  <form class="comment-form" @submit.prevent="onSubmit">
    <!-- Toast -->
    <div v-if="toast.show" class="toast" :class="toast.type" role="status" aria-live="polite">
      {{ toast.msg }}
    </div>

    <!-- User info (anonymous only) -->
    <div v-if="!hasJwt" class="section">
      <div class="section-title">{{ $t("form.userInfo") }}</div>

      <div class="grid3">
        <div class="form-group">
          <label class="form-label">
            {{ $t("form.userName") }} <span class="req">*</span>
          </label>
          <input
            ref="userRef"
            class="form-input"
            :class="{ invalid: !!errors.user_name }"
            v-model.trim="form.user_name"
            type="text"
            :disabled="submitting"
            placeholder=""
          />
          <p v-if="errors.user_name" class="error-text">{{ errors.user_name }}</p>
        </div>

        <div class="form-group">
          <label class="form-label">
            {{ $t("form.email") }} <span class="req">*</span>
          </label>
          <input
            class="form-input"
            :class="{ invalid: !!errors.email }"
            v-model.trim="form.email"
            type="email"
            :disabled="submitting"
            placeholder=""
          />
          <p v-if="errors.email" class="error-text">{{ errors.email }}</p>
        </div>

        <div class="form-group">
          <label class="form-label">{{ $t("form.homepage") }}</label>
          <input
            class="form-input"
            :class="{ invalid: !!errors.homepage }"
            v-model.trim="form.homepage"
            type="url"
            :disabled="submitting"
            placeholder="https://homepage.example"
          />
          <p v-if="errors.homepage" class="error-text">{{ errors.homepage }}</p>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="section">
      <div class="section-title">{{ $t("form.content") }}</div>

      <div class="form-group">
        <div class="toolbar comment-toolbar">
          <div class="toolbar-left">
            <button
              class="tool"
              type="button"
              @click="insertTag('i')"
              :disabled="submitting"
              :title="$t('form.tags.iTitle')"
            >
              [i]
            </button>
            <button
              class="tool"
              type="button"
              @click="insertTag('strong')"
              :disabled="submitting"
              :title="$t('form.tags.strongTitle')"
            >
              [strong]
            </button>
            <button
              class="tool"
              type="button"
              @click="insertTag('code')"
              :disabled="submitting"
              :title="$t('form.tags.codeTitle')"
            >
              [code]
            </button>
            <button
              class="tool"
              type="button"
              @click="insertTag('a')"
              :disabled="submitting"
              :title="$t('form.tags.aTitle')"
            >
              [a]
            </button>
          </div>

          <div class="tabs" role="tablist" :aria-label="$t('form.editorMode')">
            <button
              class="tab"
              type="button"
              role="tab"
              :class="{ on: editorMode === 'write' }"
              @click="editorMode = 'write'"
              :disabled="submitting"
              :aria-selected="String(editorMode === 'write')"
            >
              {{ $t("form.write") }}
            </button>
            <button
              class="tab"
              type="button"
              role="tab"
              :class="{ on: editorMode === 'preview' }"
              @click="editorMode = 'preview'"
              :disabled="submitting"
              :aria-selected="String(editorMode === 'preview')"
            >
              {{ $t("form.preview") }}
            </button>
          </div>
        </div>

        <label class="sr-only">{{ $t("form.text") }}</label>

        <textarea
          v-show="editorMode === 'write'"
          ref="textRef"
          class="form-textarea comment-textarea"
          :class="{ invalid: !!errors.text }"
          v-model="form.text"
          @keydown.enter.exact.prevent="onSubmit"
          @keydown.enter.shift.exact.stop
          rows="7"
          :disabled="submitting"
          :placeholder="$t('form.placeholder')"
        />

        <div v-show="editorMode === 'preview'" class="preview-box">
          <div v-if="!form.text.trim()" class="preview-empty">{{ $t("form.previewEmpty") }}</div>
          <div v-else class="preview-content" v-html="previewHtml"></div>
          <div v-if="previewWarning" class="preview-warn">⚠ {{ previewWarning }}</div>
        </div>

        <p v-if="errors.text" class="error-text">{{ errors.text }}</p>
      </div>
    </div>

    <!-- Security (anonymous only) -->
    <div v-if="!hasJwt" class="section">
      <div class="section-title">{{ $t("form.security") }}</div>

      <div class="form-group">
        <label class="form-label">
          {{ $t("form.captcha") }} <span class="req">*</span>
        </label>

        <div class="captcha-row">
          <img v-if="captcha.image" class="captcha-image" :src="captcha.image" :alt="$t('form.captcha')" />

          <button
            class="captcha-reload"
            type="button"
            @click="loadCaptcha"
            :disabled="submitting || captchaLoading"
            :title="$t('form.captchaReload')"
          >
            ⟳
          </button>

          <input
            class="form-input captcha-input"
            :class="{ invalid: !!errors.captcha_value }"
            v-model.trim="form.captcha_value"
            type="text"
            autocomplete="off"
            :disabled="submitting"
            :placeholder="$t('form.captchaPlaceholder')"
          />
        </div>

        <p v-if="errors.captcha_value" class="error-text">{{ errors.captcha_value }}</p>
      </div>
    </div>

    <!-- Attachments (JWT only) -->
    <div v-if="hasJwt" class="section">
      <div class="section-title">{{ $t("attachments.title") }}</div>

      <div class="form-group">
        <div
          class="dropzone attachments-dropzone"
          :class="{ disabled: submitting || !hasJwt, over: dragOver }"
          @dragenter.prevent="onDragEnter"
          @dragover.prevent="onDragOver"
          @dragleave.prevent="onDragLeave"
          @drop.prevent="onDrop"
        >
          <div class="dz-top">
            <div class="dz-title">{{ $t("attachments.dropTitle") }}</div>
            <div class="attachments-hint">Images: JPG, PNG, GIF (max 320×240). Text files: TXT (max 100 KB).</div>
            <div class="dz-sub">{{ $t("attachments.dropSub") }}</div>
          </div>

          <button
            type="button"
            class="dz-btn"
            @click="browseFiles"
            :disabled="submitting || !hasJwt"
            :title="$t('attachments.chooseTitle')"
          >
            {{ $t("attachments.chooseBtn") }}
          </button>

          <input
            ref="fileInput"
            class="file-hidden"
            type="file"
            multiple
            accept=".jpg,.jpeg,.png,.gif,.webp,.txt"
            @change="onFilesSelected"
            :disabled="submitting || !hasJwt"
          />
        </div>

        <div class="hint-text">{{ $t("attachments.allowed") }}</div>

        <div v-if="hasJwt && selectedFiles.length" class="files-list">
          <div v-for="(f, idx) in selectedFiles" :key="idx" class="file-item">
            <div class="file-left">
              <div v-if="f.previewUrl" class="thumb" :style="{ backgroundImage: `url('${f.previewUrl}')` }"></div>
              <div v-else class="thumb txt">TXT</div>

              <div class="file-meta">
                <div class="file-name">{{ f.file.name }}</div>
                <div class="file-sub">
                  <span class="file-size">{{ formatBytes(f.file.size) }}</span>
                  <span v-if="isImageFile(f.file)" class="file-note">• {{ $t("attachments.resizeNote") }}</span>
                </div>
              </div>
            </div>

            <div class="file-right">
              <span v-if="f.error" class="file-error">{{ f.error }}</span>
              <button class="file-remove" type="button" @click="removeFile(idx)" :disabled="submitting" :title="$t('attachments.remove')">
                ✕
              </button>
            </div>
          </div>
        </div>

        <p v-if="errors.attachments" class="error-text">{{ errors.attachments }}</p>
      </div>
    </div>

    <!-- Actions -->
    <div class="form-actions">
      <button class="btn primary comment-submit" type="submit" :disabled="submitting || !isValid">
        <span v-if="submitting" class="spinner" aria-hidden="true"></span>
        {{ submitting ? $t("form.sending") : $t("form.send") }}
      </button>

      <button class="btn ghost" type="button" @click="$emit('cancel')" v-if="parentId !== null" :disabled="submitting">
        {{ $t("form.cancel") }}
      </button>
    </div>

    <p v-if="errors.non_field" class="error-text">{{ errors.non_field }}</p>
  </form>
</template>

<script>
import { apiGet, getAccessToken, buildUrl } from "../api/index";
import { createComment, uploadFiles } from "../api/comments";

export default {
  name: "CommentForm",
  emits: ["created", "cancel"],
  props: {
    me: { type: Object, default: null },
    parentId: { type: [Number, String, null], default: null },
    resetKey: { type: Number, default: 0 },
  },

  data() {
    return {
      parentIdInternal: null,
      submitting: false,
      captchaLoading: false,
      hasJwt: false,

      captcha: { key: "", image: "" },
      selectedFiles: [], // { file, error, previewUrl }

      errors: {},

      editorMode: "write", // write | preview
      previewWarning: "",
      dragOver: false,

      toast: { show: false, type: "success", msg: "" },
      _toastTimer: null,

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

  computed: {
    isValid() {
      const hasText = !!this.form.text?.trim();
      if (!hasText) return false;

      if (!this.hasJwt) {
        return (
          !!this.form.user_name?.trim() &&
          !!this.form.email?.trim() &&
          !!this.form.captcha_key &&
          !!this.form.captcha_value?.trim()
        );
      }
      return true;
    },

    previewHtml() {
      const { html, warning } = this.renderPreview(this.form.text || "");
      this.previewWarning = warning || "";
      return html;
    },
  },

  watch: {
    parentId: {
      immediate: true,
      handler(val) {
        this.parentIdInternal = val !== null && val !== undefined && val !== "" ? Number(val) : null;
      },
    },
    me: {
      immediate: true,
      handler() {
        this.prefillFromMe();
      },
    },
    resetKey() {
      this.resetAll();
    },
  },

  mounted() {
    this._onAuthChangedBound = () => this.onAuthChanged();

    this.syncAuth();
    this.prefillFromMe();

    if (!this.hasJwt) this.loadCaptcha();

    window.addEventListener("auth-changed", this._onAuthChangedBound);

    this.focusFirst();
  },

  beforeUnmount() {
    window.removeEventListener("auth-changed", this._onAuthChangedBound);
    this.revokeAllPreviews();
    if (this._toastTimer) clearTimeout(this._toastTimer);
  },

  methods: {
    // Toast
    showToast(type, msg) {
      this.toast = { show: true, type, msg };
      if (this._toastTimer) clearTimeout(this._toastTimer);
      this._toastTimer = setTimeout(() => {
        this.toast.show = false;
      }, 2200);
    },

    // Focus
    focusFirst() {
      this.$nextTick(() => {
        if (!this.hasJwt) this.$refs.userRef?.focus?.();
        else this.$refs.textRef?.focus?.();
      });
    },

    // Auth sync
    syncAuth() {
      this.hasJwt = !!getAccessToken();

      if (this.hasJwt) {
        this.form.captcha_key = "";
        this.form.captcha_value = "";
        this.captcha = { key: "", image: "" };
      }
    },

    prefillFromMe() {
      if (!this.hasJwt) return;

      const uname = this.me?.username || this.me?.user_name || "";
      const email = this.me?.email || "";

      if (uname) this.form.user_name = uname;
      if (email) this.form.email = email;
    },

    async resetAll() {
      this.errors = {};
      this.editorMode = "write";
      this.previewWarning = "";
      this.toast.show = false;

      this.syncAuth();

      this.form.homepage = "";
      this.form.text = "";
      this.clearFiles();

      if (!this.hasJwt) {
        this.form.user_name = "";
        this.form.email = "";
        await this.loadCaptcha();
      } else {
        this.prefillFromMe();
      }

      this.focusFirst();
    },

    onAuthChanged() {
      const was = this.hasJwt;
      this.syncAuth();

      if (!was && this.hasJwt) {
        this.errors = {};
        this.clearFiles();
        this.prefillFromMe();
      }

      if (was && !this.hasJwt) {
        this.clearFiles();
        this.form.user_name = "";
        this.form.email = "";
        this.loadCaptcha();
      }

      this.focusFirst();
    },

    // CAPTCHA
    async loadCaptcha() {
      this.captchaLoading = true;
      try {
        const data = await apiGet("/api/comments/captcha/");
        const key = data?.key || "";
        const img = data?.image || data?.image_url || "";

        this.captcha.key = key;
        this.captcha.image = buildUrl(img);

        this.form.captcha_key = key;
        this.form.captcha_value = "";
      } catch (e) {
        this.errors.captcha_value = this.$t("form.captchaLoadFail");
      } finally {
        this.captchaLoading = false;
      }
    },

    // Tag insertion
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

        if (start === end) {
          const pos = start + open.length;
          el.setSelectionRange(pos, pos);
        } else {
          const selStart = start + open.length;
          const selEnd = selStart + selected.length;
          el.setSelectionRange(selStart, selEnd);
        }
      });
    },

    // Attachments UI
    browseFiles() {
      this.syncAuth();
      if (!this.hasJwt) return;
      this.$refs.fileInput?.click?.();
    },

    onDragEnter() {
      if (this.submitting || !this.hasJwt) return;
      this.dragOver = true;
    },
    onDragOver() {
      if (this.submitting || !this.hasJwt) return;
      this.dragOver = true;
    },
    onDragLeave() {
      this.dragOver = false;
    },
    onDrop(e) {
      this.dragOver = false;
      this.syncAuth();
      if (!this.hasJwt || this.submitting) return;

      const files = Array.from(e?.dataTransfer?.files || []);
      this.ingestFiles(files);

      const inp = this.$refs.fileInput;
      if (inp) inp.value = "";
    },

    onFilesSelected(e) {
      this.syncAuth();
      if (!this.hasJwt) {
        this.clearFiles();
        return;
      }
      const files = Array.from(e?.target?.files || []);
      this.ingestFiles(files);
    },

    ingestFiles(files) {
      this.revokeAllPreviews();

      this.selectedFiles = (files || []).map((file) => {
        const err = this.validateFile(file);
        const previewUrl = err ? null : this.isImageFile(file) ? URL.createObjectURL(file) : null;
        return { file, error: err, previewUrl };
      });
    },

    isImageFile(file) {
      const name = (file?.name || "").toLowerCase();
      return (
        name.endsWith(".jpg") ||
        name.endsWith(".jpeg") ||
        name.endsWith(".png") ||
        name.endsWith(".gif") ||
        name.endsWith(".webp")
      );
    },

    validateFile(file) {
      const name = (file?.name || "").toLowerCase();
      const isTxt = name.endsWith(".txt");
      const isImg = this.isImageFile(file);

      if (!isTxt && !isImg) return this.$t("attachments.errType");
      if (isTxt && file.size > 100 * 1024) return this.$t("attachments.errTxtSize");
      return null;
    },

    removeFile(idx) {
      const item = this.selectedFiles[idx];
      if (item?.previewUrl) URL.revokeObjectURL(item.previewUrl);
      this.selectedFiles.splice(idx, 1);
    },

    clearFiles() {
      this.revokeAllPreviews();
      this.selectedFiles = [];
      const inp = this.$refs.fileInput;
      if (inp) inp.value = "";
    },

    revokeAllPreviews() {
      for (const f of this.selectedFiles || []) {
        if (f?.previewUrl) URL.revokeObjectURL(f.previewUrl);
      }
    },

    formatBytes(bytes) {
      if (!bytes) return "0 B";
      const k = 1024;
      const sizes = ["B", "KB", "MB", "GB"];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      const val = bytes / Math.pow(k, i);
      return `${val.toFixed(i === 0 ? 0 : 1)} ${sizes[i]}`;
    },

    // Preview renderer (safe)
    escapeHtml(s) {
      return String(s)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    },

    renderPreview(raw) {
      const text = String(raw || "");
      const escaped = this.escapeHtml(text);

      const pairs = ["i", "strong", "code", "a"];
      let warning = "";

      for (const t of pairs) {
        const openCount = (text.match(new RegExp(`\\[${t}\\]`, "g")) || []).length;
        const closeCount = (text.match(new RegExp(`\\[\\/${t}\\]`, "g")) || []).length;
        if (openCount !== closeCount) {
          warning = this.$t("form.tagsUnclosed");
          break;
        }
      }

      let html = escaped;

      html = html.replace(/\[code\]([\s\S]*?)\[\/code\]/g, (_m, p1) => `<pre class="p-code"><code>${p1}</code></pre>`);
      html = html.replace(/\[strong\]([\s\S]*?)\[\/strong\]/g, "<strong>$1</strong>");
      html = html.replace(/\[i\]([\s\S]*?)\[\/i\]/g, "<em>$1</em>");

      html = html.replace(/\[a\]([\s\S]*?)\[\/a\]/g, (_m, p1) => {
        const rawText = String(p1 || "").trim();
        const looksUrl = /^https?:\/\/[^\s]+$/i.test(rawText);
        if (looksUrl) {
          const href = rawText.replaceAll('"', "%22");
          return `<a class="p-link" href="${href}" target="_blank" rel="noopener noreferrer">${rawText}</a>`;
        }
        return `<span class="p-link p-link-disabled">${rawText}</span>`;
      });

      html = html.replace(/\n/g, "<br />");
      return { html, warning };
    },

    // Errors
    mapApiErrors(err) {
      const payload = err?.payload;
      if (payload && typeof payload === "object") {
        const out = {};
        for (const [k, v] of Object.entries(payload)) {
          out[k] = Array.isArray(v) ? v.join(" ") : String(v);
        }
        return out;
      }
      return { non_field: this.$t("form.requestFailed") };
    },

    // Submit
    async onSubmit() {
      this.errors = {};
      this.syncAuth();
      this.prefillFromMe();

      if (!this.form.text?.trim()) this.errors.text = this.$t("form.errTextRequired");

      if (!this.hasJwt) {
        if (!this.form.user_name?.trim()) this.errors.user_name = this.$t("form.errUserRequired");
        if (!this.form.email?.trim()) this.errors.email = this.$t("form.errEmailRequired");
        if (!this.form.captcha_key || !this.form.captcha_value) {
          this.errors.captcha_value = this.$t("form.errCaptchaRequired");
        }
      }

      if (Object.keys(this.errors).length) {
        this.showToast("error", this.$t("form.validationFailed"));
        return;
      }

      this.submitting = true;

      try {
        const payload = {
          user_name: this.form.user_name,
          email: this.form.email,
          homepage: this.form.homepage || null,
          text: this.form.text,
        };

        const parentId = this.parentIdInternal;

        // JWT: do not send empty user_name/email (backend uses token)
        if (this.hasJwt) {
          if (!String(payload.user_name || "").trim()) delete payload.user_name;
          if (!String(payload.email || "").trim()) delete payload.email;
        } else {
          payload.captcha_key = this.form.captcha_key;
          payload.captcha_value = this.form.captcha_value;
        }

        if (parentId !== null && parentId !== undefined) {
          payload.parent = Number(parentId);
        }

        if (this.hasJwt && this.selectedFiles.length) {
          const okFiles = this.selectedFiles.filter((f) => !f.error).map((f) => f.file);
          if (okFiles.length) {
            const up = await uploadFiles(okFiles);
            const attachment_ids = up.attachment_ids || [];
            const upload_key = up.upload_key || null;

            if (attachment_ids.length && upload_key) {
              payload.attachment_ids = attachment_ids;
              payload.upload_key = upload_key;
            }
          }
        }

        const created = await createComment(payload);

        // reset fields
        this.form.text = "";
        this.form.homepage = "";
        this.editorMode = "write";
        this.previewWarning = "";
        this.clearFiles();

        if (!this.hasJwt) await this.loadCaptcha();

        this.showToast("success", this.$t("form.commentAdded"));
        this.$emit("created", { created, parentId });
      } catch (err) {
        this.errors = this.mapApiErrors(err);

        if (!this.hasJwt && (this.errors.captcha_value || this.errors.captcha_key)) {
          await this.loadCaptcha();
        }

        this.showToast("error", this.$t("form.requestFailed"));
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

  background: var(--surface-3);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);

  /* softer text */
  color: var(--text-muted, #6b7280);
}

.toast {
  border-radius: 14px;
  padding: 10px 12px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  font-weight: 800;
  font-size: 13px;
}
.toast.success {
  border-color: rgba(34, 197, 94, 0.35);
  background: rgba(34, 197, 94, 0.10);
}
.toast.error {
  border-color: rgba(255, 90, 120, 0.35);
  background: rgba(255, 90, 120, 0.10);
}

.section {
  border: 1px solid var(--border);
  background: var(--surface-2);
  border-radius: 16px;
  padding: 14px;
}

.section-title {
  font-weight: 950;
  color: var(--text);
  letter-spacing: 0.2px;

  padding-bottom: 10px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--border);
}

.req {
  color: var(--danger, #ff5a78);
  font-weight: 900;
}

.grid3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}
@media (max-width: 920px) {
  .grid3 {
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
  margin-bottom: 6px;
}

.form-input,
.form-textarea {
  background: var(--input-bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 9px 12px;
  font-size: 14px;
  outline: none;
}

.form-input:focus,
.form-textarea:focus {
  border-color: rgba(96, 165, 250, 0.55);
  box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.16);
}

.invalid {
  border-color: rgba(255, 90, 120, 0.55) !important;
  box-shadow: 0 0 0 2px rgba(255, 90, 120, 0.14) !important;
}

.form-textarea {
  resize: vertical;
  min-height: 130px;
}

.error-text {
  color: var(--danger, #ff5a78);
  font-size: 13px;
  line-height: 1.25;
}

.hint-text {
  color: var(--muted);
  font-size: 13px;
}

.comment-form .hint-text,
.comment-form .error-text {
  color: var(--muted);
}
.comment-form .error-text {
  color: var(--danger, #ff5a78);
}

.comment-form input::placeholder,
.comment-form textarea::placeholder {
  color: rgba(148, 163, 184, 0.9);
}

/* Toolbar */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.toolbar-left {
  display: inline-flex;
  gap: 8px;
}

.tool {
  min-width: 72px;
  text-align: center;
  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.10);
  border-radius: 12px;
  padding: 7px 10px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 900;
  color: var(--text);
}
.tool:hover {
  background: rgba(96, 165, 250, 0.16);
}
.tool:active {
  transform: translateY(1px);
}
.tool:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

html[data-theme="light"] .tool {
  background: rgba(37, 99, 235, 0.08);
  border-color: rgba(37, 99, 235, 0.25);
}
html[data-theme="light"] .tool:hover {
  background: rgba(37, 99, 235, 0.12);
}

.tabs {
  display: inline-flex;
  border: 1px solid var(--border);
  border-radius: 999px;
  overflow: hidden;
  background: var(--surface);
}

.tab {
  padding: 7px 12px;
  font-weight: 900;
  font-size: 13px;
  cursor: pointer;
  background: transparent;
  border: none;
  color: var(--text);
}
.tab.on {
  background: rgba(96, 165, 250, 0.14);
}
html[data-theme="light"] .tab.on {
  background: rgba(37, 99, 235, 0.10);
}
.tab:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Preview */
.preview-box {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 14px;
  padding: 12px;
  min-height: 140px;
}

.preview-empty {
  color: var(--muted);
  font-size: 13px;
}

.preview-warn {
  margin-top: 10px;
  font-size: 13px;
  color: var(--muted);
}

.preview-content {
  color: var(--text);
  line-height: 1.45;
}

.p-code {
  margin: 8px 0;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  overflow: auto;
  font-size: 13px;
}

.p-link {
  color: rgba(96, 165, 250, 0.95);
  text-decoration: underline;
  font-weight: 800;
}
html[data-theme="light"] .p-link {
  color: rgba(37, 99, 235, 0.95);
}
.p-link-disabled {
  text-decoration: none;
  opacity: 0.85;
  cursor: default;
}

/* Dropzone */
.dropzone {
  border: 1px dashed rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.08);
  border-radius: 16px;
  padding: 12px 14px;
  min-height: 72px;

  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

html[data-theme="light"] .dropzone {
  border-color: rgba(37, 99, 235, 0.25);
  background: rgba(37, 99, 235, 0.06);
}

.dropzone.over {
  background: rgba(96, 165, 250, 0.14);
}

.dropzone.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dz-top {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dz-title {
  font-weight: 950;
  color: var(--text);
  font-size: 14px;
  line-height: 1.2;
}

.dz-sub {
  margin-top: 2px;
  font-size: 12px;
  color: var(--muted);
}

.dz-btn {
  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.14);
  border-radius: 14px;
  padding: 9px 14px;
  cursor: pointer;
  font-weight: 900;
  color: var(--text);
  white-space: nowrap;
}
.dz-btn:hover {
  background: rgba(96, 165, 250, 0.18);
}
.dz-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

html[data-theme="light"] .dz-btn {
  background: rgba(37, 99, 235, 0.10);
  border-color: rgba(37, 99, 235, 0.28);
}

.file-hidden {
  display: none;
}

/* Files list */
.files-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 10px;
  background: var(--surface);
}

.file-left {
  display: flex;
  gap: 10px;
  align-items: center;
  min-width: 0;
}

.thumb {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  background-size: cover;
  background-position: center;
  flex: 0 0 auto;
}

.thumb.txt {
  display: grid;
  place-items: center;
  font-weight: 950;
  font-size: 12px;
  color: var(--muted);
}

.file-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.file-name {
  font-weight: 950;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 520px;
}
@media (max-width: 760px) {
  .file-name {
    max-width: 240px;
  }
}

.file-sub {
  font-size: 13px;
  color: var(--muted);
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.file-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-error {
  color: var(--danger, #ff5a78);
  font-size: 13px;
  white-space: nowrap;
}

.file-remove {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  color: var(--text);
  opacity: 0.85;
}
.file-remove:hover {
  opacity: 1;
}

/* Captcha */
.captcha-row {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.captcha-image {
  height: 42px;
  width: auto;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--input-bg);
}

.captcha-reload {
  width: 42px;
  height: 42px;
  padding: 0;
  border-radius: 12px;

  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.10);
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
  height: 42px;
  padding-top: 0;
  padding-bottom: 0;
}

/* Actions */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.btn {
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  border-radius: 16px;
  padding: 12px 18px;
  cursor: pointer;
  font-weight: 950;
  min-width: 210px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn.primary {
  border: 1px solid rgba(96, 165, 250, 0.35);
  background: rgba(96, 165, 250, 0.16);
}
.btn.primary:hover {
  background: rgba(96, 165, 250, 0.20);
}
.btn.ghost {
  background: transparent;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* spinner */
.spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: rgba(255, 255, 255, 0.95);
  animation: spin 0.75s linear infinite;
}
html[data-theme="light"] .spinner {
  border-color: rgba(15, 23, 42, 0.20);
  border-top-color: rgba(15, 23, 42, 0.75);
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* a11y */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
