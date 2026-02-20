import React from 'react';

const OrderStatusBadge = ({ status }) => {
  let activeStyle = 'bg-slate-100 text-slate-500 border-slate-200';

  if (!status) return null;

  // بررسی هوشمند کلمات داخل وضعیت (فارسی یا انگلیسی)
  if (status.includes('انتظار') || status.includes('بررسی') || status.includes('Pending') || status.includes('اولیه')) {
    activeStyle = 'bg-warning/10 text-warning border-warning/20';
  } else if (status.includes('انجام') || status.includes('پردازش') || status.includes('طراحی') || status.includes('Processing')) {
    activeStyle = 'bg-info/10 text-info border-info/20';
  } else if (status.includes('تکمیل') || status.includes('موفق') || status.includes('آماده') || status.includes('Completed')) {
    activeStyle = 'bg-success/10 text-success border-success/20';
  } else if (status.includes('لغو') || status.includes('رد') || status.includes('Canceled')) {
    activeStyle = 'bg-error/10 text-error border-error/20';
  }

  return (
    <span className={`badge badge-sm border font-medium py-3 px-3 ${activeStyle}`}>
      {status}
    </span>
  );
};

export default OrderStatusBadge;