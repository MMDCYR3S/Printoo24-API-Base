// مسیر: src/App.jsx
import React from "react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner"; 
import AppRoutes from "@/routes/AppRoutes";

// حذف ایمپورت App.css برای جلوگیری از تداخل استایل‌های پیش‌فرض Vite
// import "./App.css"; 

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppRoutes />
        <Toaster position="top-center" richColors closeButton />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;