import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthLayout from './app/features/auth/AuthLayout';
import LoginPage from './app/features/auth/LoginPage';
import RegisterPage from './app/features/auth/RegisterPage';
import VerifyPage from './app/features/auth/VerifyPage';
import MainLayout from './app/layouts/MainLayout';
import HomePage from './app/pages/Home';


// فعلا یک صفحه اصلی ساده میذاریم تا بعدا که گفتی چی توش باشه
const Home = () => <div className="p-10 text-center text-2xl">صفحه اصلی فروشگاه (مخصوص مشتری)</div>;

function App() {
  return (
    <BrowserRouter>
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
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;