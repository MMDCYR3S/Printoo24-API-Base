import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthLayout from './app/features/auth/AuthLayout';
import LoginPage from './app/features/auth/LoginPage';
import RegisterPage from './app/features/auth/RegisterPage';
import VerifyPage from './app/features/auth/VerifyPage';
import MainLayout from './app/layouts/MainLayout';
import HomePage from './app/pages/Home';
import ProfileDashboard from './app/features/profile/ProfileDashboard';
import WalletPage from './app/features/profile/WalletPage';
import MyOrdersPage from './app/features/profile/MyOrdersPage';
import OrderDetailPage from './app/features/profile/OrderDetailPage';
import AddressPage from './app/features/profile/AddressPage';

// admin pages
import AdminLayout from './app/features/admin/layout/AdminLayout';
import AdminGuard from './app/features/auth/AdminGuard';

// import AuthLayout from './app/features/auth/AuthLayout';

// Admin Pages (Imports) 👈 ایمپورت‌های جدید
import AdminDashboard from './app/features/admin/features/dashboard/AdminDashboard';
import ProductListPage from './app/features/admin/features/products/ProductListPage';
import ProductCreatePage from './app/features/admin/features/products/ProductEditorPage';
import ProductSizesPage from './app/features/admin/features/products/ProductSizesPage';
import ProductQuantitiesPage from './app/features/admin/features/products/ProductQuantitiesPage';
import CategoryListPage from './app/features/admin/features/categories/CategoryListPage';
import SubCategoryPage from './app/features/admin/features/categories/SubCategoryPage';
import OrderListPage from './app/features/admin/features/orders/OrderListPage';
import OrderCreatePage from './app/features/admin/features/orders/OrderCreatePage';
import UserListPage from './app/features/admin/features/users/UsersListPage';
import MessageListPage from './app/features/admin/features/messages/MessageListPage';
import SliderSettingsPage from './app/features/admin/features/settings/SliderSettingsPage';
import ModalSettingsPage from './app/features/admin/features/settings/ModalSettingsPage';


const AdminOrders = () => <div className="text-xl">لیست سفارشات اینجا میاد...</div>;

// فعلا یک صفحه اصلی ساده میذاریم تا بعدا که گفتی چی توش باشه
const Home = () => <div className="p-10 text-center text-2xl">صفحه اصلی فروشگاه (مخصوص مشتری)</div>;

function App() {
  return (
    <BrowserRouter >
      <Routes>
        {/* مسیرهای احراز هویت */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify" element={<VerifyPage />} />
        </Route>

        {/* صفحه اصلی مشتری */}

        <Route path="*" element={<Navigate to="/" replace />} />

        {/* ریدایرکت هر آدرس پرتی به خانه */}
        <Route element={<MainLayout />}>
        <Route path="/" element={<HomePage />} />

        {/* صفحات پنل مشتری */}
        <Route path='/profile' element={<ProfileDashboard />} />
        <Route path="profile/orders" element={<MyOrdersPage />} />
        <Route path="profile/orders/:id" element={<OrderDetailPage />} />
        <Route path="profile/wallet" element={<WalletPage />} />
        <Route path="profile/addresses" element={<AddressPage />} />


        </Route>

        {/* 🔐 مسیرهای ادمین */}
        <Route path="/admin" element={<AdminGuard />}>
          <Route element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="orders" element={<AdminOrders />} />
            {/* بقیه روت‌های ادمین اینجا اضافه میشن */}
          {/* محصولات */}
            <Route path="products">
              <Route index element={<ProductListPage />} />
              <Route path="create" element={<ProductCreatePage />} />
              <Route path="sizes" element={<ProductSizesPage />} />
              <Route path="quantities" element={<ProductQuantitiesPage />} />
              {/* برای ویرایش بعدا اینو اضافه میکنیم: path="edit/:id" */}
            </Route>

            {/* دسته‌بندی‌ها */}
            <Route path="categories">
              <Route index element={<CategoryListPage />} />
              <Route path="sub" element={<SubCategoryPage />} />
            </Route>

            {/* سفارشات */}
            <Route path="orders">
              <Route index element={<OrderListPage />} />
              <Route path="create" element={<OrderCreatePage />} />
              {/* دیتیل سفارش: path=":id" */}
            </Route>

            {/* کاربران */}
            <Route path="users" element={<UserListPage />} />

            {/* پیام‌ها */}
            <Route path="messages" element={<MessageListPage />} />

            {/* تنظیمات */}
            <Route path="settings">
              <Route path="sliders" element={<SliderSettingsPage />} />
              <Route path="modals" element={<ModalSettingsPage />} />
            </Route>
            
          </Route>
        </Route>



      </Routes>
    </BrowserRouter>
  );
}

export default App;