// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Layouts
import AdminLayout from './app/features/admin/layout/AdminLayout';
import AdminGuard from './app/features/auth/AdminGuard'; // مسیر گارد رو چک کن
import AuthLayout from './app/features/auth/AuthLayout';
import MainLayout from './app/layouts/MainLayout';

// Public & User Pages
import HomePage from './app/pages/Home';
import LoginPage from './app/features/auth/LoginPage';
import RegisterPage from './app/features/auth/RegisterPage';
import VerifyPage from './app/features/auth/VerifyPage';
import ProfileDashboard from './app/features/profile/ProfileDashboard';
import WalletPage from './app/features/profile/WalletPage';
import MyOrdersPage from './app/features/profile/MyOrdersPage';
import OrderDetailPage from './app/features/profile/OrderDetailPage';
import AddressPage from './app/features/profile/AddressPage';

// Admin Pages
import AdminDashboard from './app/features/admin/features/dashboard/AdminDashboard';

// Admin > Products
import ProductListPage from './app/features/admin/features/products/ProductListPage';
import ProductEditorPage from './app/features/admin/features/products/ProductEditorPage';
import ProductDetailPage from './app/features/admin/features/products/ProductDetailPage'; // ✅ New
import ProductSizesPage from './app/features/admin/features/products/ProductSizesPage';
import ProductQuantitiesPage from './app/features/admin/features/products/ProductQuantitiesPage';

// Admin > Categories
import CategoryListPage from './app/features/admin/features/categories/CategoryListPage';
import CategoryUpsertPage from './app/features/admin/features/categories/CategoryUpsertPage';
import CategoryDetailPage from './app/features/admin/features/categories/CategoryDetailPage';
import SubCategoryPage from './app/features/admin/features/categories/SubCategoryPage';

// Admin > Orders
import OrderListPage from './app/features/admin/features/orders/OrderListPage';
import OrderCreatePage from './app/features/admin/features/orders/OrderCreatePage';
import AdminOrderDetailsPage from './app/features/admin/features/orders/OrderDetailsPage'; // اسم رو اصلاح کردم تا با کاربر قاطی نشه

// Admin > Users & Others
import UserListPage from './app/features/admin/features/users/UsersListPage';
import MessageListPage from './app/features/admin/features/messages/MessageListPage';
import SliderSettingsPage from './app/features/admin/features/settings/SliderSettingsPage';
import ModalSettingsPage from './app/features/admin/features/settings/ModalSettingsPage';
import ProvincesPage from './app/features/admin/features/locations/ProvincesPage';
import CitiesPage from './app/features/admin/features/locations/CitiesPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Toaster position="top-center" reverseOrder={false} />
        
        <Routes>
          {/* --- Auth Routes --- */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify" element={<VerifyPage />} />
          </Route>

          {/* --- Admin Panel (Protected) --- */}
          <Route path="/admin" element={<AdminGuard />}>
            <Route element={<AdminLayout />}>
              
              <Route index element={<AdminDashboard />} />
              
              {/* Products Management */}
              <Route path="products">
                <Route index element={<ProductListPage />} />
                <Route path="create" element={<ProductEditorPage />} />
                <Route path="edit/:id" element={<ProductEditorPage />} />
                <Route path=":id" element={<ProductDetailPage />} /> {/* ✅ Detail Route */}
                <Route path="sizes" element={<ProductSizesPage />} />
                <Route path="quantities" element={<ProductQuantitiesPage />} />
              </Route>

              {/* Categories Management */}
              <Route path="categories">
                <Route index element={<CategoryListPage />} />
                <Route path="create" element={<CategoryUpsertPage />} />
                <Route path="edit/:id" element={<CategoryUpsertPage />} />
                <Route path=":id" element={<CategoryDetailPage />} />
                <Route path="sub" element={<SubCategoryPage />} />
              </Route>

              {/* Orders Management */}
              <Route path="orders">
                <Route index element={<OrderListPage />} />
                <Route path="create" element={<OrderCreatePage />} />
                <Route path=":id" element={<AdminOrderDetailsPage />} />
              </Route>

              {/* Users & Locations */}
              <Route path="users" element={<UserListPage />} />
              <Route path="provinces" element={<ProvincesPage />} />
              <Route path="cities" element={<CitiesPage />} />
              
              {/* Messages & Settings */}
              <Route path="messages" element={<MessageListPage />} />
              <Route path="settings/sliders" element={<SliderSettingsPage />} />
              <Route path="settings/modals" element={<ModalSettingsPage />} />

            </Route>
          </Route>

          {/* --- Public / User Panel --- */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<HomePage />} />
            
            {/* User Profile */}
            <Route path="profile">
              <Route index element={<ProfileDashboard />} />
              <Route path="orders" element={<MyOrdersPage />} />
              <Route path="orders/:id" element={<OrderDetailPage />} />
              <Route path="wallet" element={<WalletPage />} />
              <Route path="addresses" element={<AddressPage />} />
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />

        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;