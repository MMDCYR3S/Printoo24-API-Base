import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import './index.css'
import App from './App.jsx'

// ایجاد کلاینت برای مدیریت کش سرور
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false, // جلوگیری از درخواست تکراری با هر کلیک
      retry: 1, // در صورت خطا فقط یک بار تلاش مجدد کن
    },
  },
})

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <Toaster position="top-center" reverseOrder={false} />
    </QueryClientProvider>
  </StrictMode>,
)