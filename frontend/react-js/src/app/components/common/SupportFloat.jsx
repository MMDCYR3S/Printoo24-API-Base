// src/app/components/common/SupportFloat.jsx
import { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';

const SupportFloat = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    // روی موبایل: bottom-[88px] تا بالای sticky bar باشه
    // روی دسکتاپ: bottom-6 معمولی
    <div className="fixed bottom-[88px] lg:bottom-6 left-4 lg:left-6 z-40 flex flex-col items-center gap-3">

      {/* لینک‌ها — با انیمیشن ظاهر/محو */}
      <div
        className={`flex flex-col items-center gap-3 transition-all duration-300 origin-bottom ${
          isOpen
            ? 'opacity-100 translate-y-0 pointer-events-auto'
            : 'opacity-0 translate-y-4 pointer-events-none'
        }`}
      >
        {/* واتساپ */}
        <a
          href="https://wa.me/9647762278666"
          target="_blank"
          rel="noreferrer"
          title="WhatsApp"
          className="group relative flex items-center"
        >
          {/* label */}
          <span className="absolute left-14 bg-white text-slate-700 text-xs font-bold px-2.5 py-1 rounded-lg shadow-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-slate-100">
            WhatsApp
          </span>
          <button className="w-12 h-12 rounded-full bg-[#25D366] hover:bg-[#20bd5a] border-none shadow-lg shadow-[#25D366]/40 hover:-translate-y-0.5 active:scale-95 transition-all flex items-center justify-center">
            <svg viewBox="0 0 24 24" className="w-6 h-6 fill-white" xmlns="http://www.w3.org/2000/svg">
              <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.248-.57-.397m-5.475 7.013h-.016c-2.01 0-3.978-.543-5.698-1.576l-.409-.245-4.234 1.109 1.129-4.126-.266-.423c-1.12-1.776-1.71-3.83-1.71-5.942 0-6.176 5.025-11.201 11.207-11.201 2.993 0 5.808 1.165 7.923 3.282 2.116 2.116 3.28 4.933 3.28 7.926.001 6.177-5.023 11.2-11.206 11.196"/>
            </svg>
          </button>
        </a>

        {/* تلگرام */}
        <a
          href="https://t.me/printoo24"
          target="_blank"
          rel="noreferrer"
          title="Telegram"
          className="group relative flex items-center"
        >
          <span className="absolute left-14 bg-white text-slate-700 text-xs font-bold px-2.5 py-1 rounded-lg shadow-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-slate-100">
            Telegram
          </span>
          <button className="w-12 h-12 rounded-full bg-[#229ED9] hover:bg-[#1e8dbf] border-none shadow-lg shadow-[#229ED9]/40 hover:-translate-y-0.5 active:scale-95 transition-all flex items-center justify-center">
            <svg viewBox="0 0 24 24" className="w-6 h-6 fill-white" xmlns="http://www.w3.org/2000/svg">
              <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 11.944 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
            </svg>
          </button>
        </a>
      </div>

      {/* دکمه toggle اصلی */}
      <button
        onClick={() => setIsOpen(o => !o)}
        className={`w-16 h-16 rounded-full border-none shadow-xl transition-all duration-300 active:scale-95 flex items-center justify-center ${
          isOpen
            ? 'bg-slate-700 hover:bg-slate-600 shadow-slate-400/30 rotate-0'
            : 'bg-primary/70 hover:brightness-110 shadow-primary/40'
        }`}
        title="پشتیبانی"
      >
        <span className={`transition-all duration-300 ${isOpen ? 'rotate-90 scale-110' : 'rotate-0'}`}>
          {isOpen
            ? <X size={20} className="text-white" />
            : <MessageCircle size={40} className="text-white" />
          }
        </span>
      </button>

    </div>
  );
};

export default SupportFloat;