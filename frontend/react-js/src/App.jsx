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


const AdminDashboard = () => <div className="text-2xl font-bold">به پنل مدیریت خوش آمدید 👋</div>;
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
          </Route>
        </Route>


      </Routes>
    </BrowserRouter>
  );
}

export default App;