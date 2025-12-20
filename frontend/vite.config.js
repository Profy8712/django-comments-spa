import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 5173,

    // IMPORTANT:
    // Browser talks to http://localhost:5173
    // Vite (inside Docker) proxies API requests to backend container.
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
      },
      "/captcha": {
        target: "http://backend:8000",
        changeOrigin: true,
      },
      "/media": {
        target: "http://backend:8000",
        changeOrigin: true,
      },
    },
  },
});
