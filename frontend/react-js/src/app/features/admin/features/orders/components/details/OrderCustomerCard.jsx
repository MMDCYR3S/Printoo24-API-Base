import React from 'react';
import { User, MapPin, Phone, Building2 } from 'lucide-react';

const OrderCustomerCard = ({ order }) => {
  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
        <div className="p-2 bg-slate-100 rounded-xl text-slate-600">
          <User size={20} />
        </div>
        <div>
          <h3 className="font-bold text-slate-800">{order.recipient_name || order.user_info || 'مشتری ناشناس'}</h3>
          <p className="text-xs text-slate-500">اطلاعات تحویل‌گیرنده</p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex items-center gap-3 text-sm">
          <Phone size={16} className="text-slate-400" />
          <span className="text-slate-600 font-medium">{order.recipient_phone || 'بدون شماره'}</span>
        </div>
        
        {order.company_name && (
          <div className="flex items-center gap-3 text-sm">
            <Building2 size={16} className="text-slate-400" />
            <span className="text-slate-600">{order.company_name}</span>
          </div>
        )}

        <div className="flex items-start gap-3 text-sm bg-slate-50 p-3 rounded-xl border border-slate-100">
          <MapPin size={18} className="text-primary shrink-0 mt-0.5" />
          <div className="space-y-1">
             <p className="text-slate-700 font-bold leading-relaxed">آدرس ارسال:</p>
             <p className="text-slate-600 leading-relaxed text-xs">
               {order.address_detail || 'آدرسی ثبت نشده است'}
             </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderCustomerCard;