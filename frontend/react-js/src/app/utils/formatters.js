export const formatCurrency = (value) => {
  if (value === null || value === undefined) return "0";
  // تبدیل رشته به عدد و حذف اعشار با Math.floor
  const numericValue = Math.floor(Number(value));
  // جدا کردن با کاما (هزارگان)
  return numericValue.toLocaleString('en-US'); 
};