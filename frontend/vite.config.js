// frontend/vite.config.js
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

function proxyLogger(name) {
  return {
    configure: (proxy) => {
      proxy.on("error", (err, req) => {
        console.log(`[proxy:${name}] error`, err?.message, req?.url);
      });
      proxy.on("proxyReq", (proxyReq, req) => {
        console.log(`[proxy:${name}] ->`, req?.method, req?.url);
      });
      proxy.on("proxyRes", (proxyRes, req) => {
        console.log(
          `[proxy:${name}] <-`,
          proxyRes?.statusCode,
          req?.method,
          req?.url
        );
      });
    },
  };
}

export default defineConfig({
  plugins: [vue()],

  server: {
    // Docker: allow access outside container
    host: true, // same as 0.0.0.0
    port: 5173,
    strictPort: true,

    // Proxy all backend traffic to Django container
    proxy: {
      // REST API
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
        secure: false,
        xfwd: true,
        // keep same path
        rewrite: (path) => path,
        ...proxyLogger("api"),
      },

      // CAPTCHA endpoints + images
      "/captcha": {
        target: "http://backend:8000",
        changeOrigin: true,
        secure: false,
        xfwd: true,
        rewrite: (path) => path,
        ...proxyLogger("captcha"),
      },

      // Uploaded media
      "/media": {
        target: "http://backend:8000",
        changeOrigin: true,
        secure: false,
        xfwd: true,
        rewrite: (path) => path,
        ...proxyLogger("media"),
      },

      // WebSocket
      "/ws": {
        target: "ws://backend:8000",
        ws: true,
        changeOrigin: true,
        secure: false,
        ...proxyLogger("ws"),
      },
    },
  },

  // Correct file watching inside Docker (Windows / WSL / Git Bash)
  watch: {
    usePolling: true,
    interval: 200,
  },

  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: false,
  },
});
