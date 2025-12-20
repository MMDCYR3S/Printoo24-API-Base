import clsx from 'clsx';

const OrderStatusBadge = ({ status }) => {
  // نگاشت وضعیت به رنگ‌ها (باید با خروجی دقیق API تنظیم شود)
  const styles = {
    'Pending': 'bg-warning/10 text-warning border-warning/20',
    'Processing': 'bg-info/10 text-info border-info/20',
    'Completed': 'bg-success/10 text-success border-success/20',
    'Canceled': 'bg-error/10 text-error border-error/20',
    // پیش‌فرض
    'default': 'bg-slate-100 text-slate-500 border-slate-200'
  };

  // نگاشت متن فارسی (اختیاری)
  const labels = {
    'Pending': 'در انتظار',
    'Processing': 'در حال انجام',
    'Completed': 'تکمیل شده',
    'Canceled': 'لغو شده',
  };

  const activeStyle = styles[status] || styles['default'];
  const label = labels[status] || status;

  return (
    <span className={clsx("badge badge-sm border font-medium py-3 px-3", activeStyle)}>
      {label}
    </span>
  );
};

export default OrderStatusBadge;