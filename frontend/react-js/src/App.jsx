// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// Layouts
import AdminLayout from './app/features/admin/layout/AdminLayout';
import AdminGuard from './app/features/auth/AdminGuard';
import AuthLayout from './app/features/auth/AuthLayout';
import MainLayout from './app/layouts/MainLayout';

// Public & User Pages
import HomePage from './app/pages/Home';
import ShopPage from './app/features/shop/ShopPage'; // <--- 1. ایمپورت صفحه فروشگاه
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
import ProductListPage from './app/features/admin/features/products/ProductListPage';
import ProductEditorPage from './app/features/admin/features/products/ProductEditorPage';
import ProductDetailPage from './app/features/admin/features/products/ProductDetailPage';
import ProductQuantitiesPage from './app/features/admin/features/products/ProductQuantitiesPage';
import ProductSizesPage from './app/features/admin/features/products/ProductSizesPage';
import OrderCreatePage from './app/features/admin/features/orders/OrderCreatePage';
import AdminOrderListPage from './app/features/admin/features/orders/OrderListPage';
import AdminOrderDetailsPage from './app/features/admin/features/orders/OrderDetailsPage';
import UserListPage from './app/features/admin/features/users/UsersListPage';
import ProvincesPage from './app/features/admin/features/locations/ProvincesPage';
import CitiesPage from './app/features/admin/features/locations/CitiesPage';
import MessageListPage from './app/features/admin/features/messages/MessageListPage';
import SliderSettingsPage from './app/features/admin/features/settings/SliderSettingsPage';
import ModalSettingsPage from './app/features/admin/features/settings/ModalSettingsPage';

// Admin Categories
import CategoryListPage from './app/features/admin/features/categories/CategoryListPage';
import CategoryUpsertPage from './app/features/admin/features/categories/CategoryUpsertPage';
import SubCategoryPage from './app/features/admin/features/categories/SubCategoryPage';


// ایجاد کلاینت React Query
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
          
          {/* --- Admin Routes (Protected) --- */}
          <Route path="/admin" element={<AdminGuard />}>
            <Route element={<AdminLayout />}>
              <Route index element={<AdminDashboard />} />
              
              {/* Products */}
              <Route path="products" element={<ProductListPage />} />
              <Route path="products/new" element={<ProductEditorPage />} />
              <Route path="products/:id/edit" element={<ProductEditorPage />} />
              <Route path="products/:id" element={<ProductDetailPage />} />
              <Route path="products/:id/quantities" element={<ProductQuantitiesPage />} />
              <Route path="products/:id/sizes" element={<ProductSizesPage />} />

              {/* Categories */}
              <Route path="categories" element={<CategoryListPage />} />
              <Route path="categories/new" element={<CategoryUpsertPage />} />
              <Route path="categories/:id/edit" element={<CategoryUpsertPage />} />
              <Route path="categories/:id/subs" element={<SubCategoryPage />} />

              {/* Orders */}
              <Route path="orders">
                <Route index element={<AdminOrderListPage />} />
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

          {/* --- Auth Routes --- */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify" element={<VerifyPage />} />
          </Route>

          {/* --- Public / User Panel --- */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<HomePage />} />
            
            {/* 2. روت جدید فروشگاه */}
            <Route path="/shop" element={<ShopPage />} /> 
            
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