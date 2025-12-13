// src/app/components/layout/Footer.jsx
import { Phone, MapPin, Clock } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-slate-950 text-slate-300 pt-16 pb-8 mt-auto">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 mb-12">
          
          {/* ستون اول: درباره و نقشه */}
          <div className="col-span-1 md:col-span-2 space-y-6">
            <div>
              <div className="text-3xl font-black text-white mb-4">
                Printoo<span className="text-neutral">24</span>
              </div>
              <p className="text-lg leading-relaxed font-medium text-slate-400 max-w-2xl">
                شریک تجاری شما در چاپ. حذف واسطه‌ها، قیمت واقعی و کیفیت تضمین شده برای همکاران در کردستان عراق.
              </p>
            </div>
            
            {/* نقشه */}
            <div className="rounded-2xl overflow-hidden h-64 bg-slate-700 relative border-2 border-slate-600">
               {/* در اینجا لینک iframe لوکیشن خودت را قرار بده */}
              <iframe 
                src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3239.962073919865!2d51.388973!3d35.689197!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zMzXCsDQxJzIxLjEiTiA1McKwMjMnMjAuMyJF!5e0!3m2!1sen!2s!4v1631234567890!5m2!1sen!2s" 
                width="100%" 
                height="100%" 
                style={{border:0}} 
                allowFullScreen="" 
                loading="lazy" 
                className="opacity-80 hover:opacity-100 transition-opacity grayscale hover:grayscale-0"
              ></iframe>
              <div className="absolute bottom-4 right-4 bg-white text-slate-900 px-4 py-2 rounded-lg text-sm font-bold shadow-lg pointer-events-none">
                دفتر مرکزی: تهران (جهت نمونه)
              </div>
            </div>
          </div>

          {/* ستون دوم: اطلاعات تماس */}
          <div>
            <h4 className="text-2xl font-bold text-white mb-8 flex items-center gap-3">
              <span className="w-2 h-6 bg-neutral rounded-full"></span>
              اطلاعات تماس
            </h4>
            <ul className="space-y-6">
              <li className="flex items-start gap-4">
                <MapPin className="text-neutral mt-1 shrink-0" />
                <span className="text-lg font-medium">سلیمانیه، خیابان سالم، پاساژ...</span>
              </li>
              <li className="flex items-start gap-4">
                 <Phone className="text-green-500 mt-1 shrink-0" />
                 <div className="flex flex-col">
                    <a href="tel:+9647700000000" className="text-2xl font-black text-white hover:text-green-400 transition-colors" dir="ltr">
                      +964 770 000 0000
                    </a>
                    <span className="text-sm text-green-500 font-bold">(واتساپ و تماس)</span>
                 </div>
              </li>
              <li className="flex items-start gap-4 pt-4 border-t border-slate-700">
                <Clock className="text-slate-400 mt-1 shrink-0" />
                <div>
                  <span className="block text-slate-400 text-sm">ساعات کاری:</span>
                  <span className="text-lg font-bold text-white">شنبه تا پنجشنبه، ۹ صبح تا ۶ عصر</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <div className=" text-center text-slate-500 pt-8 border-t border-slate-700 text-sm font-medium">
         تمامی حقوق برای Printoo24 محفوظ است 
        </div>
      </div>
    </footer>
  );
};

export default Footer;