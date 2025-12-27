<template>
  <transition name="lightbox-fade" appear>
    <div
      v-if="modelValue"
      class="lightbox-backdrop"
      @click.self="close"
    >
      <div class="lightbox-content">
        <button class="lightbox-close" type="button" @click="close" aria-label="Close">
          ✕
        </button>

        <!-- image -->
        <img
          v-if="type === 'image'"
          :src="src"
          :alt="alt || 'Attachment preview'"
          class="lightbox-image"
        />

        <!-- text -->
        <pre v-else-if="type === 'text'" class="lightbox-text">{{ textContent }}</pre>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, required: true },
  src: { type: String, default: "" },
  alt: { type: String, default: "" },
  type: { type: String, default: "image" }, // "image" | "text"
  textContent: { type: String, default: "" }
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
  padding: 16px;
}

.lightbox-content {
  position: relative;
  width: min(92vw, 980px);
  max-height: 92vh;
  background: #0b1120;
  border-radius: 12px;
  padding: 0.75rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.65);
  transform-origin: center;
  transform: scale(1);
}

.lightbox-image {
  display: block;
  width: 100%;
  height: auto;
  max-height: 86vh;
  object-fit: contain;
  border-radius: 8px;
}

.lightbox-text {
  width: 100%;
  max-height: 86vh;
  overflow: auto;
  color: #e5e7eb;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", "Courier New", monospace;
  white-space: pre-wrap;
}

.lightbox-close {
  position: absolute;
  top: 8px;
  right: 10px;
  border: none;
  background: transparent;
  color: #e5e7eb;
  font-size: 1.4rem;
  cursor: pointer;
}

/* animation */
.lightbox-fade-enter-active,
.lightbox-fade-leave-active {
  transition: opacity 0.25s ease;
}

.lightbox-fade-enter-active .lightbox-content,
.lightbox-fade-leave-active .lightbox-content {
  transition: transform 0.25s ease;
}

.lightbox-fade-enter-from,
.lightbox-fade-leave-to {
  opacity: 0;
}

.lightbox-fade-enter-from .lightbox-content,
.lightbox-fade-leave-to .lightbox-content {
  transform: scale(0.88);
}
</style>
