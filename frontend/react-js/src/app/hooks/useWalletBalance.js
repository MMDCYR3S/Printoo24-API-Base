import { useState, useEffect } from 'react';
import { profileService } from '../services/profileService'; // مسیر را در صورت نیاز تنظیم کنید

export const useWalletBalance = (isLoggedIn) => {
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBalance = async () => {
      // اگر لاگین نبود، اصلاً ریکوئست نمی‌زنیم
      if (!isLoggedIn) {
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        const data = await profileService.getWalletBalance();
        // مقداری که API می‌دهد در کلید decimal است
        setBalance(data.decimal);
        setError(null);
      } catch (err) {
        console.error("خطا در دریافت موجودی کیف پول:", err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchBalance();
  }, [isLoggedIn]);

  return { balance, loading, error };
};