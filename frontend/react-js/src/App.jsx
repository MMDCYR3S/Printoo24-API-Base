// src/App.jsx
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

// موقت
import DesignUploadPage from './app/features/shop/components/DesignUploadPage';
import CartPage from './app/features/shop/CartPage'
import CheckoutPage from './app/features/shop/CheckoutPage';


// --- Layouts & Guards ---
import MainLayout from './app/layouts/MainLayout';
import AuthLayout from './app/features/auth/AuthLayout';
import AdminLayout from './app/features/admin/layout/AdminLayout';
import AdminGuard from './app/features/auth/AdminGuard';

// --- Public Pages ---
import HomePage from './app/pages/Home';
import ShopPage from './app/features/shop/ShopPage';
import PublicProductDetailPage from './app/features/shop/ProductDetailPage';

// --- Auth Pages ---
import LoginPage from './app/features/auth/LoginPage';
import RegisterPage from './app/features/auth/RegisterPage';
import VerifyPage from './app/features/auth/VerifyPage';

// --- Profile Pages ---
import ProfileDashboard from './app/features/profile/ProfileDashboard';
import MyOrdersPage from './app/features/profile/MyOrdersPage';
import OrderDetailPage from './app/features/profile/OrderDetailPage';
import WalletPage from './app/features/profile/WalletPage';
import AddressPage from './app/features/profile/AddressPage';

// --- Admin Pages ---
import AdminDashboard from './app/features/admin/features/dashboard/AdminDashboard';

// Admin > Products
import ProductListPage from './app/features/admin/features/products/ProductListPage';
import ProductEditorPage from './app/features/admin/features/products/ProductEditorPage';
import AdminProductDetailPage from './app/features/admin/features/products/ProductDetailPage';
import ProductQuantitiesPage from './app/features/admin/features/products/ProductQuantitiesPage';
import ProductSizesPage from './app/features/admin/features/products/ProductSizesPage';

// Admin > Categories
import CategoryListPage from './app/features/admin/features/categories/CategoryListPage';
import CategoryUpsertPage from './app/features/admin/features/categories/CategoryUpsertPage';
import SubCategoryPage from './app/features/admin/features/categories/SubCategoryPage';
import CategoryDetailPage from './app/features/admin/features/categories/CategoryDetailPage'

// Admin > Orders
import OrderCreatePage from './app/features/admin/features/orders/OrderCreatePage';
import AdminOrderListPage from './app/features/admin/features/orders/OrderListPage';
import AdminOrderDetailsPage from './app/features/admin/features/orders/OrderDetailsPage';

// Admin > Users & Locations
import UserListPage from './app/features/admin/features/users/UsersListPage';
import ProvincesPage from './app/features/admin/features/locations/ProvincesPage';
import CitiesPage from './app/features/admin/features/locations/CitiesPage';
import CustomerDetailPage from './app/features/admin/features/users/CustomerDetailPage'; 

// Admin > Messages & Settings
import MessageListPage from './app/features/admin/features/messages/MessageListPage';
import SliderSettingsPage from './app/features/admin/features/settings/SliderSettingsPage';
import ModalSettingsPage from './app/features/admin/features/settings/ModalSettingsPage';

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
        
        <Routes >
          
          {/* =========================================
              ADMIN ROUTES (Protected)
             ========================================= */}
          <Route path="/admin" element={<AdminGuard />}>
            <Route element={<AdminLayout />}>
              <Route index element={<AdminDashboard />} />
              
              {/* === Products (اصلاح شده و نهایی) === */}
              <Route path="products" element={<ProductListPage />} />
              
              {/* 1. اولویت اول: ساخت محصول جدید */}
              <Route path="products/create" element={<ProductEditorPage />} /> 
              <Route path="products/new" element={<Navigate to="create" replace />} />
              
              {/* 2. اولویت دوم: ویرایش محصول (اصلاح آدرس برای هماهنگی با دکمه‌ها) */}
              {/* قبلاً :id/edit بود که با دکمه‌های شما فرق داشت */}
              <Route path="products/edit/:id" element={<ProductEditorPage />} />
              
              <Route path="products/quantities" element={<ProductQuantitiesPage />} />
              <Route path="products/sizes" element={<ProductSizesPage />} />
              
              {/* 3. اولویت آخر: جزئیات محصول (مسیر متغیر) */}
              <Route path="products/:id" element={<AdminProductDetailPage />} />

              {/* Categories */}
              <Route path="categories" element={<CategoryListPage />} />
              <Route path="categories/new" element={<CategoryUpsertPage />} />
              <Route path="categories/edit/:id/" element={<CategoryUpsertPage />} />
              <Route path="categories/:id/subs" element={<SubCategoryPage />} />
              <Route path="categories/:id/" element={<CategoryDetailPage />} />
              <Route path="edit/:id" element={<CategoryUpsertPage />} />

              {/* Orders */}
              <Route path="orders">
                <Route index element={<AdminOrderListPage />} />
                <Route path="create" element={<OrderCreatePage />} />
                <Route path=":id" element={<AdminOrderDetailsPage />} />
              </Route>

              {/* Users & Locations */}
              <Route path="users" element={<UserListPage />} />
              <Route path="users/:id" element={<CustomerDetailPage />} />
              <Route path="provinces" element={<ProvincesPage />} />
              <Route path="cities" element={<CitiesPage />} />
              
              {/* Messages & Settings */}
              <Route path="messages" element={<MessageListPage />} />
              <Route path="settings/sliders" element={<SliderSettingsPage />} />
              <Route path="settings/modals" element={<ModalSettingsPage />} />
            </Route>
          </Route>

          {/* AUTH ROUTES */}
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify" element={<VerifyPage />} />
          </Route>

          {/* PUBLIC ROUTES */}
          <Route element={<MainLayout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/shop" element={<ShopPage />} />
            <Route path="/product/:slug" element={<PublicProductDetailPage />} />
            
            <Route path="profile">
              <Route index element={<ProfileDashboard />} />
              <Route path="orders" element={<MyOrdersPage />} />
              <Route path="orders/:id" element={<OrderDetailPage />} />
              <Route path="wallet" element={<WalletPage />} />
              <Route path="addresses" element={<AddressPage />} />
            </Route>




<Route path="/cart/upload/:itemId" element={<DesignUploadPage />} />
<Route path="/cart" element={<CartPage />} />
<Route path="/checkout" element={<CheckoutPage />} />


          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />

        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;