import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true
    },
    proxy: {
      // هر درخواستی که با /api/admin شروع بشه میره به بکند ادمین
      '/api/admin': {
        target: 'http://admin_site:8010', // دقت کن: از اسم سرویس داکر استفاده کردیم
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/admin/, '') // اگر بکند پیشوند api نداره این خط لازمه
      },
      // هر درخواستی که با /api/customer شروع بشه میره به بکند مشتری
      '/api/customer': {
        target: 'http://customer_site:9010',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/customer/, '')
      }
    }
  }
})
