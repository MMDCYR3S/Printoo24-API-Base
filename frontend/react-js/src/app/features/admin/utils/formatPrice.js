// src/app/utils/formatPrice.js
export const formatPrice = (price) => {
  if (!price) return '0';
  // تبدیل به عدد و حذف اعشار اضافی اگر نیاز است
  const num = typeof price === 'string' ? parseFloat(price) : price;
  return new Intl.NumberFormat('EN').format(num);
};
