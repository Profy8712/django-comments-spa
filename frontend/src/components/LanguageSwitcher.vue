<template>
  <div class="lang-switch" ref="root">
    <button
      type="button"
      class="lang-btn"
      @click="toggle"
      :title="$t('lang.change')"
      aria-haspopup="listbox"
      :aria-expanded="open ? 'true' : 'false'"
    >
      🌐
      <span class="lang-cur">{{ locale.toUpperCase() }}</span>
    </button>

    <div v-if="open" class="lang-menu" role="listbox">
      <button
        v-for="l in langs"
        :key="l.code"
        type="button"
        role="option"
        class="lang-item"
        :class="{ on: locale === l.code }"
        @click="set(l.code)"
      >
        <span class="code">{{ l.code.toUpperCase() }}</span>
        <span class="label">{{ l.label }}</span>
      </button>
    </div>
  </div>
</template>

<script>
import { useI18n } from "vue-i18n";

export default {
  name: "LanguageSwitcher",
  setup() {
    const { locale, t } = useI18n({ useScope: "global" });

    const langs = [
      { code: "en", label: "English" },
      { code: "de", label: "Deutsch" },
      { code: "uk", label: "Українська" },
      { code: "ru", label: "Русский" },
    ];

    return { locale, t, langs };
  },
  data() {
    return { open: false };
  },
  mounted() {
    this._onDocClick = (e) => {
      if (!this.$refs.root) return;
      if (!this.$refs.root.contains(e.target)) this.open = false;
    };
    document.addEventListener("click", this._onDocClick);
  },
  beforeUnmount() {
    document.removeEventListener("click", this._onDocClick);
  },
  methods: {
    toggle() {
      this.open = !this.open;
    },
    set(lang) {
      this.locale = lang; // locale is a ref proxied by Vue in templates/options
      localStorage.setItem("lang", lang);
      this.open = false;
    },
  },
};
</script>

<style scoped>
.lang-switch {
  position: relative;
  display: inline-flex;
  align-items: center;
}

/* main button */
.lang-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--border, #cbd5e1);
  background: var(--surface, transparent);
  cursor: pointer;
  color: var(--text, #0f172a);
  font-weight: 900;
}

.lang-cur {
  font-size: 12px;
  opacity: 0.85;
}

/* dropdown */
.lang-menu {
  position: absolute;
  right: 0;
  top: 110%;
  z-index: 50;
  min-width: 180px;

  border-radius: 14px;
  border: 1px solid var(--border, #cbd5e1);
  background: var(--surface, #fff);
  box-shadow: 0 14px 26px rgba(0, 0, 0, 0.18);
  padding: 6px;
}

.lang-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;

  border: none;
  background: transparent;
  cursor: pointer;

  padding: 8px 10px;
  border-radius: 12px;
  color: var(--text, #0f172a);
  text-align: left;
}

.lang-item:hover {
  background: rgba(96, 165, 250, 0.14);
}

.lang-item.on {
  background: rgba(96, 165, 250, 0.18);
  font-weight: 950;
}

.code {
  width: 36px;
  font-weight: 950;
  opacity: 0.9;
}

.label {
  opacity: 0.95;
}
</style>
