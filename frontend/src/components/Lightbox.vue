<template>
  <transition name="lightbox-fade">
    <div
      v-if="modelValue"
      class="lightbox-backdrop"
      @click.self="close"
    >
      <div class="lightbox-content">
        <button class="lightbox-close" type="button" @click="close">
          ✕
        </button>

        <!-- картинка -->
        <img
          v-if="type === 'image'"
          :src="src"
          :alt="alt || 'Attachment preview'"
          class="lightbox-image"
        />

        <!-- текстовый файл -->
        <pre
          v-else-if="type === 'text'"
          class="lightbox-text"
        >{{ textContent }}</pre>
      </div>
    </div>
  </transition>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: Boolean, required: true },
  src: { type: String, default: "" },      // для картинок
  alt: { type: String, default: "" },
  type: { type: String, default: "image" }, // "image" или "text"
  textContent: { type: String, default: "" } // для txt (если решишь грузить)
});

const emit = defineEmits(["update:modelValue"]);

function close() {
  emit("update:modelValue", false);
}
</script>

<style scoped>
.lightbox-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.lightbox-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  background: #0b1120;
  border-radius: 12px;
  padding: 0.75rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.65);
}

.lightbox-image {
  display: block;
  max-width: 80vw;
  max-height: 80vh;
  border-radius: 8px;
}

.lightbox-text {
  max-width: 80vw;
  max-height: 80vh;
  overflow: auto;
  color: #e5e7eb;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", "Courier New", monospace;
  white-space: pre-wrap;
}

.lightbox-close {
  position: absolute;
  top: 0.25rem;
  right: 0.35rem;
  border: none;
  background: transparent;
  color: #e5e7eb;
  font-size: 1.3rem;
  cursor: pointer;
}

/* анимация появления/исчезновения */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.2s ease;
}

.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}
</style>
