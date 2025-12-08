<template>
  <form class="comment-form" @submit.prevent="onSubmit">
    <h2 class="form-title">New comment</h2>

    <!-- User name -->
    <div class="form-group">
      <label class="form-label" for="user_name">User name *</label>
      <input
        id="user_name"
        v-model.trim="form.user_name"
        type="text"
        class="form-input"
        :class="{ 'has-error': errors.user_name }"
        placeholder="John Doe"
      />
      <p v-if="errors.user_name" class="error-text">{{ errors.user_name }}</p>
    </div>

    <!-- Email -->
    <div class="form-group">
      <label class="form-label" for="email">Email *</label>
      <input
        id="email"
        v-model.trim="form.email"
        type="email"
        class="form-input"
        :class="{ 'has-error': errors.email }"
        placeholder="john@example.com"
      />
      <p v-if="errors.email" class="error-text">{{ errors.email }}</p>
    </div>

    <!-- Homepage -->
    <div class="form-group">
      <label class="form-label" for="homepage">Homepage</label>
      <input
        id="homepage"
        v-model.trim="form.homepage"
        type="url"
        class="form-input"
        placeholder="https://example.com"
      />
    </div>

    <!-- Text -->
    <div class="form-group">
      <label class="form-label" for="text">Text *</label>

      <div class="toolbar">
        <button
          v-for="btn in tagButtons"
          :key="btn.tag"
          type="button"
          class="toolbar-btn"
          @click="wrapWithTag(btn.tag)"
        >
          {{ btn.label }}
        </button>
      </div>

      <textarea
        id="text"
        v-model="form.text"
        class="form-textarea"
        :class="{ 'has-error': errors.text }"
        rows="6"
        placeholder="Enter your comment..."
        data-enable-grammarly="false"
      ></textarea>

      <p class="hint-text">
        Allowed pseudo-tags: [i], [strong], [code], [a]
      </p>
      <p v-if="errors.text" class="error-text">{{ errors.text }}</p>
    </div>

    <!-- Attachments -->
    <div class="form-group">
      <label class="form-label" for="attachments">
        Attach files (images or .txt)
      </label>
      <input
        id="attachments"
        type="file"
        class="form-input"
        multiple
        accept=".jpg,.jpeg,.png,.gif,.txt"
        @change="onFilesChange"
      />

      <p class="hint-text">
        Images: JPG, PNG, GIF (will be resized to max 320x240).<br />
        Text: TXT ≤ 100 KB.
      </p>

      <ul v-if="selectedFiles.length" class="files-list">
        <li
          v-for="file in selectedFiles"
          :key="file.id"
          class="files-list-item"
        >
          <span>{{ file.file.name }} ({{ formatSize(file.file.size) }})</span>
          <span v-if="file.error" class="error-text"> — {{ file.error }}</span>
        </li>
      </ul>

      <p v-if="errors.attachments" class="error-text">
        {{ errors.attachments }}
      </p>
    </div>

    <!-- CAPTCHA -->
    <div class="form-group">
      <label class="form-label" for="captcha">CAPTCHA *</label>

      <div class="captcha-row">
        <div class="captcha-image-wrapper">
          <button
            type="button"
            class="captcha-reload"
            :disabled="captchaLoading"
            @click="reloadCaptcha"
          >
            <span v-if="captchaLoading">Loading...</span>
            <img
              v-else-if="captchaImage"
              :src="captchaImage"
              alt="CAPTCHA"
              class="captcha-image"
            />
            <span v-else>Load</span>
          </button>
        </div>

        <input
          id="captcha"
          v-model.trim="captchaValue"
          type="text"
          class="form-input captcha-input"
          :class="{ 'has-error': errors.captcha }"
          placeholder="Enter text from image"
        />
      </div>

      <p v-if="errors.captcha" class="error-text">{{ errors.captcha }}</p>
    </div>

    <!-- Actions -->
    <div class="form-actions">
      <button
        type="button"
        class="btn btn-secondary"
        @click="togglePreview"
      >
        {{ showPreview ? "Hide preview" : "Show preview" }}
      </button>

      <button
        type="submit"
        class="btn btn-primary"
        :disabled="submitting"
      >
        {{ submitting ? "Sending..." : "Send comment" }}
      </button>
    </div>

    <!-- Preview block -->
    <div v-if="showPreview" class="preview-card">
      <h3 class="preview-title">Preview</h3>

      <div class="preview-meta">
        <span><strong>User:</strong> {{ form.user_name || "—" }}</span>
        <span><strong>Email:</strong> {{ form.email || "—" }}</span>
        <span><strong>Homepage:</strong> {{ form.homepage || "—" }}</span>
      </div>

      <div
        class="preview-text"
        v-html="renderedPreview"
      ></div>
    </div>
  </form>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { loadCaptcha } from "@/api/captcha";
import { createComment } from "@/api/comments";
import { uploadAttachment } from "@/api/attachments";

const props = defineProps({
  parentId: {
    type: Number,
    default: null,
  },
});

const emit = defineEmits(["created"]);

const form = reactive({
  user_name: "",
  email: "",
  homepage: "",
  text: "",
});

const errors = reactive({
  user_name: null,
  email: null,
  text: null,
  captcha: null,
  attachments: null,
});

const tagButtons = [
  { tag: "i", label: "[i]" },
  { tag: "strong", label: "[strong]" },
  { tag: "code", label: "[code]" },
  { tag: "a", label: "[a]" },
];

const showPreview = ref(false);
const submitting = ref(false);

// captcha state
const captchaImage = ref(null);
const captchaKey = ref(null);
const captchaValue = ref("");
const captchaLoading = ref(false);

// attachments
const selectedFiles = ref([]); // [{ id, file, error }]
let fileIdCounter = 0;

function resetErrors() {
  errors.user_name = null;
  errors.email = null;
  errors.text = null;
  errors.captcha = null;
  errors.attachments = null;
}

function onFilesChange(event) {
  const files = Array.from(event.target.files || []);
  selectedFiles.value = [];
  errors.attachments = null;

  const allowedExt = [".jpg", ".jpeg", ".png", ".gif", ".txt"];
  const maxTxtSize = 100 * 1024;

  for (const f of files) {
    const lower = f.name.toLowerCase();
    const ext = lower.slice(lower.lastIndexOf("."));

    let error = null;

    if (!allowedExt.includes(ext)) {
      error = "Unsupported file type.";
    } else if (ext === ".txt" && f.size > maxTxtSize) {
      error = "TXT file must be ≤ 100 KB.";
    }

    selectedFiles.value.push({
      id: ++fileIdCounter,
      file: f,
      error,
    });
  }

  const anyValid = selectedFiles.value.some((f) => !f.error);
  if (!anyValid && selectedFiles.value.length) {
    errors.attachments = "All selected files are invalid.";
  }
}

function validateForm() {
  resetErrors();
  let valid = true;

  if (!form.user_name.trim()) {
    errors.user_name = "User name is required.";
    valid = false;
  }

  if (!form.email.trim()) {
    errors.email = "Email is required.";
    valid = false;
  } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email.trim())) {
    errors.email = "Email is not valid.";
    valid = false;
  }

  if (!form.text.trim()) {
    errors.text = "Text is required.";
    valid = false;
  }

  if (!captchaValue.value.trim()) {
    errors.captcha = "CAPTCHA is required.";
    valid = false;
  }

  if (!captchaKey.value) {
    errors.captcha = "CAPTCHA is not loaded.";
    valid = false;
  }

  const invalidOnly =
    selectedFiles.value.length > 0 &&
    !selectedFiles.value.some((f) => !f.error);

  if (invalidOnly) {
    errors.attachments = "All selected files are invalid.";
    valid = false;
  }

  return valid;
}

async function reloadCaptcha() {
  try {
    captchaLoading.value = true;
    const data = await loadCaptcha();

    // Support both { key, image } and { captcha_key, captcha_image_url }
    captchaKey.value = data.key ?? data.captcha_key;
    captchaImage.value = data.image ?? data.captcha_image_url;
    captchaValue.value = "";
    errors.captcha = null;
  } catch (e) {
    console.error(e);
    errors.captcha = "Failed to load CAPTCHA.";
    captchaImage.value = null;
  } finally {
    captchaLoading.value = false;
  }
}

onMounted(() => {
  reloadCaptcha();
});

function wrapWithTag(tag) {
  const open = `[${tag}]`;
  const close = `[/${tag}]`;

  if (!form.text) {
    form.text = `${open}${close}`;
    return;
  }

  form.text += `${open}${close}`;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function applyPseudoTags(str) {
  let safe = escapeHtml(str);

  safe = safe.replace(/\[i](.+?)\[\/i]/gis, "<i>$1</i>");
  safe = safe.replace(/\[strong](.+?)\[\/strong]/gis, "<strong>$1</strong>");
  safe = safe.replace(/\[code](.+?)\[\/code]/gis, "<code>$1</code>");
  safe = safe.replace(
    /\[a(?:\s+href="([^"]*)")?](.+?)\[\/a]/gis,
    (_, href, text) => {
      const url = escapeHtml((href || text || "").trim());
      const content = escapeHtml(text.trim());
      if (!url) return content;
      return `<a href="${url}" rel="nofollow noopener" target="_blank">${content}</a>`;
    }
  );

  return safe;
}

const renderedPreview = computed(() => {
  if (!form.text.trim()) return "<em>No text</em>";
  return applyPseudoTags(form.text);
});

function togglePreview() {
  showPreview.value = !showPreview.value;
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

async function onSubmit() {
  if (!validateForm()) {
    return;
  }

  submitting.value = true;

  try {
    const payload = {
      user_name: form.user_name.trim(),
      email: form.email.trim(),
      homepage: form.homepage.trim() || null,
      text: form.text,
      captcha_key: captchaKey.value,
      captcha_value: captchaValue.value.trim(),
    };

    if (props.parentId) {
      payload.parent = props.parentId;
    }

    const comment = await createComment(payload);

    const validFiles = selectedFiles.value.filter((f) => !f.error);
    for (const f of validFiles) {
      try {
        await uploadAttachment(comment.id, f.file);
      } catch (e) {
        console.error("Failed to upload file:", f.file.name, e);
      }
    }

    form.user_name = "";
    form.email = "";
    form.homepage = "";
    form.text = "";
    captchaValue.value = "";
    selectedFiles.value = [];
    showPreview.value = false;
    resetErrors();

    emit("created", comment);
    await reloadCaptcha();
  } catch (e) {
    console.error(e);
    if (e && typeof e === "object") {
      if (Array.isArray(e.captcha_value)) {
        errors.captcha = e.captcha_value.join(" ");
      } else if (Array.isArray(e.non_field_errors)) {
        errors.captcha = e.non_field_errors.join(" ");
      } else {
        errors.captcha = "Failed to submit comment.";
      }
    } else {
      errors.captcha = "Failed to submit comment.";
    }
    await reloadCaptcha();
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.comment-form {
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
}

.form-title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.4rem;
}

.form-input,
.form-textarea {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #d4d4d8;
  padding: 0.6rem 0.75rem;
  font-size: 0.95rem;
}

.form-textarea {
  resize: vertical;
}

.form-input.has-error,
.form-textarea.has-error {
  border-color: #ef4444;
}

.error-text {
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.hint-text {
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 0.35rem;
}

.toolbar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.toolbar-btn {
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  font-size: 0.8rem;
  cursor: pointer;
}

.toolbar-btn:hover {
  background: #e5f0ff;
}

.captcha-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.captcha-image-wrapper {
  display: flex;
  align-items: center;
}

.captcha-reload {
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  padding: 0.2rem;
  background: #f9fafb;
  cursor: pointer;
  min-width: 96px;
  min-height: 40px;
}

.captcha-image {
  display: block;
  max-width: 120px;
  max-height: 60px;
}

.captcha-input {
  flex: 1;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn {
  border-radius: 999px;
  padding: 0.6rem 1.4rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background: #2563eb;
  color: #ffffff;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: default;
}

.btn-secondary {
  background: #f3f4f6;
  color: #111827;
}

.preview-card {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
}

.preview-title {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.preview-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.preview-text {
  padding: 0.75rem;
  border-radius: 8px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  font-size: 0.95rem;
}

.files-list {
  list-style: none;
  padding-left: 0;
  margin-top: 0.5rem;
}

.files-list-item {
  font-size: 0.85rem;
}
</style>
