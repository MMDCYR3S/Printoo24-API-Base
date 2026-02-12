import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from "path"
import { fileURLToPath } from "url"

// ✅ فیکس کردن مشکل __dirname در حالت ES Module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: true,
    port: 5174,
    watch: {
      usePolling: true
    },
    proxy: {
      '/api/v1': {
        target: 'http://127.0.0.1:8010', 
        changeOrigin: true,
        secure: false,
      },
    }
  },
})