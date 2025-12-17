import { useQuery } from '@tanstack/react-query';
import { profileService } from '../../services/profileService';
import { ArrowUpRight, ArrowDownLeft, Calendar, Wallet } from 'lucide-react';

const WalletPage = () => {
  const { data: history, isLoading } = useQuery({
    queryKey: ['wallet-history'],
    queryFn: profileService.getWalletHistory,
  });

  // تابع کمکی برای فرمت قیمت
  const formatPrice = (price) => new Intl.NumberFormat('fa-IQ').format(price);

  if (isLoading) return <div className="p-10 text-center"><span className="loading loading-spinner"></span></div>;

  // فلت کردن آرایه اگر ساختار [[...]] باشد (طبق داکیومنت شما)
  const transactions = Array.isArray(history?.[0]) ? history[0] : (history || []);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
        <Wallet className="text-primary" />
        تاریخچه تراکنش‌ها
      </h1>

      <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
        {transactions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="table w-full">
              <thead className="bg-slate-50 text-slate-500">
                <tr>
                  <th>نوع تراکنش</th>
                  <th>مبلغ (IQD)</th>
                  <th>موجودی پس از تراکنش</th>
                  <th>تاریخ</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((item) => {
                  const isDeposit = parseFloat(item.amount) > 0;
                  return (
                    <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                      <td>
                        <div className="flex items-center gap-2">
                          <div className={`p-2 rounded-xl ${isDeposit ? 'bg-emerald-100 text-emerald-600' : 'bg-red-100 text-red-600'}`}>
                            {isDeposit ? <ArrowDownLeft size={16} /> : <ArrowUpRight size={16} />}
                          </div>
                          <span className="font-bold text-slate-700">{item.type_display}</span>
                        </div>
                      </td>
                      <td className={`font-black dir-ltr text-right ${isDeposit ? 'text-emerald-600' : 'text-red-600'}`}>
                        {formatPrice(item.amount)}
                      </td>
                      <td className="font-medium dir-ltr text-right text-slate-500">
                        {formatPrice(item.amount_after)}
                      </td>
                      <td className="text-slate-400 text-sm">
                        <div className="flex items-center gap-1">
                          <Calendar size={14} />
                          <span dir="ltr">{new Date(item.created_at).toLocaleDateString('fa-IR')}</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-10 text-center text-slate-400">هیچ تراکنشی یافت نشد.</div>
        )}
      </div>
    </div>
  );
};

export default WalletPage;