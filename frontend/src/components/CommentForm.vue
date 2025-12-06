<template>
  <form class="comment-form" @submit.prevent="handleSubmit">
    <div class="field">
      <label>User name *</label>
      <input v-model="form.user_name" type="text" required />
    </div>

    <div class="field">
      <label>Email *</label>
      <input v-model="form.email" type="email" required />
    </div>

    <div class="field">
      <label>Homepage</label>
      <input v-model="form.homepage" type="url" />
    </div>

    <div class="field">
      <label>Text *</label>

      <div class="toolbar">
        <button type="button" @click="wrapTag('i')">[i]</button>
        <button type="button" @click="wrapTag('strong')">[strong]</button>
        <button type="button" @click="wrapTag('code')">[code]</button>
        <button type="button" @click="insertLink">[a]</button>
      </div>

      <textarea
        v-model="form.text"
        rows="5"
        required
        placeholder="Enter your comment..."
      ></textarea>
    </div>

    <div class="field" v-if="captcha">
      <label>CAPTCHA *</label>
      <div class="captcha-row">
        <img
          :src="captcha.captcha_image_url"
          alt="captcha"
          class="captcha-image"
        />
        <button type="button" @click="reloadCaptcha">↻</button>
      </div>
      <input
        v-model="captchaText"
        type="text"
        required
        placeholder="Enter text from image"
      />
    </div>

    <p v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </p>

    <button type="submit" :disabled="loading">
      {{ loading ? "Sending..." : "Send comment" }}
    </button>
  </form>
</template>

<script>
import { fetchCaptcha, createComment } from "../api";

export default {
  name: "CommentForm",
  props: {
    parentId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      form: {
        user_name: "",
        email: "",
        homepage: "",
        text: "",
      },
      captcha: null,
      captchaText: "",
      loading: false,
      errorMessage: "",
    };
  },
  methods: {
    async loadCaptcha() {
      try {
        this.errorMessage = "";
        const data = await fetchCaptcha();
        // Because of Vite proxy, backend returns absolute or /captcha/... URL
        // We use it as is
        this.captcha = {
          captcha_key: data.captcha_key,
          captcha_image_url: data.captcha_image_url,
        };
        this.captchaText = "";
      } catch (error) {
        this.errorMessage = "Failed to load CAPTCHA.";
      }
    },
    async reloadCaptcha() {
      await this.loadCaptcha();
    },
    wrapTag(tag) {
      const open = `<${tag}>`;
      const close = `</${tag}>`;

      if (!this.form.text) {
        this.form.text = `${open}${close}`;
        return;
      }

      this.form.text += ` ${open}${close}`;
    },
    insertLink() {
      this.form.text += ' <a href="" title=""></a>';
    },
    async handleSubmit() {
      this.errorMessage = "";
      this.loading = true;

      try {
        const payload = {
          user_name: this.form.user_name,
          email: this.form.email,
          homepage: this.form.homepage || null,
          text: this.form.text,
          parent: this.parentId,
          captcha_key: this.captcha?.captcha_key,
          captcha_text: this.captchaText,
        };

        await createComment(payload);

        // Reset text only, keep username/email if you want better UX
        this.form.text = "";
        this.captchaText = "";

        // Reload CAPTCHA for next submit
        await this.loadCaptcha();

        // Notify parent
        this.$emit("created");
      } catch (err) {
        if (err && typeof err === "object") {
          if (err.captcha_text && err.captcha_text.length) {
            this.errorMessage = err.captcha_text[0];
          } else if (err.user_name && err.user_name.length) {
            this.errorMessage = err.user_name[0];
          } else if (err.text && err.text.length) {
            this.errorMessage = err.text[0];
          } else {
            this.errorMessage = "Failed to send comment.";
          }
        } else {
          this.errorMessage = "Failed to send comment.";
        }
      } finally {
        this.loading = false;
      }
    },
  },
  async mounted() {
    await this.loadCaptcha();
  },
};
</script>

<style scoped>
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.toolbar {
  margin-bottom: 0.25rem;
}

.toolbar button {
  margin-right: 0.25rem;
}

.captcha-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.captcha-image {
  border: 1px solid #ccc;
}

.error-message {
  color: red;
  font-size: 0.9rem;
}
</style>
