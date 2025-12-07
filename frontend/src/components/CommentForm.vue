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

      <!-- pseudo-tags toolbar -->
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
      />
      <p class="hint-text">
        Allowed pseudo-tags:
        [i], [strong], [code], [a]
      </p>
      <p v-if="errors.text" class="error-text">{{ errors.text }}</p>
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
      />
    </div>
  </form>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { loadCaptcha } from "@/api/captcha";
import { createComment } from "@/api/comments";

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

function resetErrors() {
  errors.user_name = null;
  errors.email = null;
  errors.text = null;
  errors.captcha = null;
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

  if (!captchaValue.trim()) {
    errors.captcha = "CAPTCHA is required.";
    valid = false;
  }

  if (!captchaKey.value) {
    errors.captcha = "CAPTCHA is not loaded.";
    valid = false;
  }

  return valid;
}

async function reloadCaptcha() {
  try {
    captchaLoading.value = true;
    const data = await loadCaptcha();
    captchaKey.value = data.key;
    captchaImage.value = data.image;
  } catch (e) {
    console.error(e);
    errors.captcha = "Failed to load CAPTCHA.";
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

  // simple append; можно доработать с выделенным текстом через textarea ref
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

  // [i]...[/i]
  safe = safe.replace(/\[i](.+?)\[\/i]/gis, "<i>$1</i>");
  // [strong]...[/strong]
  safe = safe.replace(/\[strong](.+?)\[\/strong]/gis, "<strong>$1</strong>");
  // [code]...[/code]
  safe = safe.replace(
    /\[code](.+?)\[\/code]/gis,
    "<code>$1</code>"
  );
  // [a href="..."]...[/a]  или [a]url[/a]
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

async function onSubmit() {
  if (!validateForm()) {
    if (!showPreview.value) {
      showPreview.value = false;
    }
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

    await createComment(payload);

    // reset form on success
    form.user_name = "";
    form.email = "";
    form.homepage = "";
    form.text = "";
    captchaValue.value = "";
    showPreview.value = false;
    resetErrors();

    // reload captcha for next comment
    await reloadCaptcha();
  } catch (e) {
    console.error(e);
    errors.captcha =
      e?.message || "Failed to submit comment. Please try again.";
    // тоже перезагрузим капчу на всякий случай
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
</style>
