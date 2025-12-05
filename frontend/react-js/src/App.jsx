import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import AuthLayout from './app/features/auth/AuthLayout';
import LoginPage from './app/features/auth/LoginPage';
import RegisterPage from './app/features/auth/RegisterPage';
import VerifyPage from './app/features/auth/VerifyPage';

// یک کامپوننت موقت برای داشبورد (بعدا کاملش میکنیم)
const Dashboard = () => <div className="p-10 text-center text-3xl">خوش آمدید! اینجا پنل کاربری است.</div>;

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* مسیرهای مربوط به احراز هویت */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify" element={<VerifyPage />} />
        </Route>

        {/* مسیرهای محافظت شده (بعدا گارد میگذاریم) */}
        <Route path="/dashboard" element={<Dashboard />} />

        {/* ریدایرکت پیش‌فرض */}
        <Route path="/" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;