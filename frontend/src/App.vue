<template>
  <div class="app">
    <h1>Comments SPA</h1>

    <section>
      <h2>New comment</h2>
      <CommentForm @created="onCommentCreated" />
    </section>
  </div>
</template>

<script>
import CommentForm from "./components/CommentForm.vue";

export default {
  name: "App",
  components: { CommentForm },
  methods: {
    onCommentCreated() {
      console.log("Comment created");
    },
  },
};
</script>

<style>
.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
}
</style>
