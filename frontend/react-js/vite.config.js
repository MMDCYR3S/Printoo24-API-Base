// import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'
// import tailwindcss from '@tailwindcss/vite'

// export default defineConfig({
//   plugins: [
//     react(),
//     tailwindcss(),
//   ],
  
//   // ===== تنظیمات Build برای Production ===== //
//   build: {
//     outDir: 'dist',
//     emptyOutDir: true,
//     sourcemap: false,
//     minify: 'esbuild',
//     rollupOptions: {
//       output: {
//         manualChunks: {
//           vendor: ['react', 'react-dom', 'react-router-dom'],
//         },
//       },
//     },
//   },
  
//   // ===== تنظیمات Development Server ===== //
//   server: {
//     host: true,
//     port: 5173,
//     watch: {
//       usePolling: true
//     },
//     proxy: {
//       '/api/admin': {
//         target: 'http://127.0.0.1:8010', 
//         changeOrigin: true,
//         rewrite: (path) => path.replace(/^\/api\/admin/, '')
//       },
//       '/api/customer': {
//         target: 'http://127.0.0.1:9010',
//         changeOrigin: true,
//         rewrite: (path) => path.replace(/^\/api\/customer/, '')
//       }
//     }
//   }
// })


import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true
    },
    proxy: {
      // ✅ کانفیگ جدید: تمام درخواست‌هایی که با /api/v1 شروع می‌شوند
      '/api/v1': {
        target: 'http://customer_site:9010', // آدرس واقعی بک‌اند
        changeOrigin: true,
        secure: false,
        // نکته مهم: اینجا rewrite نداریم چون بک‌اند شما خودش /api/v1 را دارد
        // یعنی درخواست /api/v1/login دقیقا به /api/v1/login در پورت 9010 می‌رسد
      },
      
      // کانفیگ ادمین (اگر نیاز دارید بماند)
      '/api/admin': {
        target: 'http://127.0.0.1:8010', 
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/admin/, '')
      }
    }
  }
})