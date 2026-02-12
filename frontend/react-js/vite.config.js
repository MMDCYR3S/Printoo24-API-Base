import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(),
  tailwindcss(),
  ],
  server: {
    host: true, // این خط برای دسترسی از بیرون کانتینر حیاتی است
    port: 5173,
    watch: {
      usePolling: true // برای اطمینان از هات‌ریلود در لینوکس
    },
    proxy: {
      // === تغییر حیاتی ===
      // چون network_mode: "host" است، باید به IP لوکال (127.0.0.1) وصل شویم
      // اسم سرویس‌ها (مثل admin_site) اینجا کار نمی‌کند
      '/api/admin': {
        target: 'http://127.0.0.1:8010', 
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/admin/, '')
      },
      '/api/customer': {
        target: 'customer_site:9010',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/customer/, '')
      }
    }
  }
})
