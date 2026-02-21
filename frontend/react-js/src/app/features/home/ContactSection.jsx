import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Phone, MapPin, Mail, Send, Instagram, Facebook } from 'lucide-react';
import { contactService } from '../../services/contactService';
import pageText from '../../lang/pages.json'

// 1. تعریف اسکیما اعتبارسنجی (Validation)
const contactSchema = z.object({
  full_name: z.string().min(3, 'لطفاً نام کامل خود را وارد کنید'),
  email: z.string().email('فرمت ایمیل صحیح نیست').optional().or(z.literal('')), // اختیاری اگر خالی بود گیر نده
  phone_number: z.string().min(10, 'شماره تماس معتبر نیست').regex(/^\d+$/, 'فقط عدد وارد کنید'),
  subject: z.string().min(3, 'موضوع پیام الزامی است'),
  message: z.string().min(10, 'متن پیام باید حداقل ۱۰ کاراکتر باشد'),
});

const ContactSection = () => {
  // 2. تنظیم فرم
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(contactSchema),
  });

  // 3. تنظیم Mutation برای ارسال به API
  const contactMutation = useMutation({
    mutationFn: contactService.sendMessage,
    onSuccess: () => {
      toast.success(pageText.home.contactSection.toastSuccess);
      reset(); // فرم را خالی کن
    },
    onError: (error) => {
      const msg = error.response?.data?.detail || pageText.home.contactSection.toastError ;
      toast.error(msg);
    }
  });

  const onSubmit = (data) => {
    contactMutation.mutate(data);
  };

  return (
    <section className="container mx-auto px-4 py-12" id="contact-us">
      <div className="grid grid-cols-1 lg:grid-cols-5 bg-white rounded-3xl shadow-xl overflow-hidden border border-base-200">
        
        {/* === بخش اطلاعات تماس (ستون سمت راست/بالا) === */}
        <div className="lg:col-span-2 bg-radial from-primary to-secondary text-white p-8 md:p-12 flex flex-col justify-between relative overflow-hidden">
          {/* پترن پس‌زمینه تزئینی */}
          <div className="absolute top-0 left-0 w-32 h-32  rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
          <div className="absolute bottom-0 right-0 w-40 h-40 bg-secondary/20 rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>

          <div className="relative z-10">
            <h3 className="text-2xl font-black mb-2">{pageText.home.contactSection.contactMethods}</h3>
            <p className="text-slate-400 text-sm mb-8">
              {pageText.home.contactSection.desc }
            </p>

            <ul className="space-y-6">
              <li className="flex items-start gap-4">
                <div className="p-3 bg-white/10 rounded-xl backdrop-blur-md text-primary-content">
                  <Phone size={24} />
                </div>
                <div>
                  <span className="block text-xs text-slate-400 mb-1">{pageText.layout.footer.whatsApp}</span>
                  <a href="tel:+9647700000000" dir="ltr" className="text-xl font-bold hover:text-primary transition-colors block">
                    +964 770 000 0000
                  </a>
                </div>
              </li>

              <li className="flex items-start gap-4">
                <div className="p-3 bg-white/10 rounded-xl backdrop-blur-md text-primary-content">
                  <MapPin size={24} />
                </div>
                <div>
                  <span className="block text-xs text-slate-400 mb-1">
               {pageText.layout.footer.office}
               </span>
                  <p className="text-sm font-medium leading-relaxed">
                   {pageText.layout.footer.fullAdress}
                  </p>
                </div>
              </li>

              <li className="flex items-start gap-4">
                <div className="p-3 bg-white/10 rounded-xl backdrop-blur-md text-primary-content">
                  <Mail size={24} />
                </div>
                <div>
                  <span className="block text-xs text-slate-400 mb-1">E-mail</span>
                  <a href="mailto:info@printoo24.com" className="text-sm font-medium hover:text-primary transition-colors">
                    info@printoo24.com
                  </a>
                </div>
              </li>
            </ul>
          </div>

          {/* شبکه‌های اجتماعی */}
          <div className="relative z-10 mt-8 pt-8 border-t border-white/10">
            <div className="flex gap-4 justify-center lg:justify-start">
              <a href="#" className="p-2 bg-white/5 hover:bg-gradient-to-tr from-purple-500 to-pink-500 rounded-lg transition-all duration-300 group">
                <Instagram size={28} className="group-hover:text-white" />
              </a>
              <a href="#" className="p-2 bg-white/5 hover:bg-blue-600 rounded-lg transition-all duration-300 group">
                <Facebook size={28} className="group-hover:text-white" />
              </a>
            </div>
          </div>
        </div>

        {/* === بخش فرم تماس (ستون سمت چپ/پایین) === */}
        <div className="lg:col-span-3 p-8 md:p-12 bg-radial from-white from-35% to-slate-200">
          <div className="max-w-lg mx-auto lg:max-w-none">
            <h2 className="text-2xl font-black text-slate-800 mb-6 flex items-center gap-2">
              <Send className="text-primary rotate-180" size={24} />
              {pageText.home.contactSection.sendMessage}
            </h2>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* نام و نام خانوادگی */}
                <div className="form-control">
                  <label className="label"><span className="label-text font-bold mb-2">{pageText.home.contactSection.fullName}</span></label>
                  <input 
                    type="text" 

                    className={`input input-bordered w-full bg-slate-50 focus:bg-white transition-colors ${errors.full_name ? 'input-error' : ''}`}
                    {...register('full_name')}
                  />
                  {errors.full_name && <span className="text-error text-xs mt-1">{errors.full_name.message}</span>}
                </div>

                {/* شماره تماس */}
                <div className="form-control">
                  <label className="label"><span className="label-text font-bold mb-2">{pageText.home.contactSection.phoneNumber}</span></label>
                  <input 
                    type="tel" 
                    placeholder="0770..." 
                    dir="ltr"
                    className={`input input-bordered w-full bg-slate-50 focus:bg-white text-right transition-colors ${errors.phone_number ? 'input-error' : ''}`}
                    {...register('phone_number')}
                  />
                  {errors.phone_number && <span className="text-error text-xs mt-1">{errors.phone_number.message}</span>}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 {/* ایمیل (اختیاری) */}
                 <div className="form-control">
                  <label className="label"><span className="label-text font-bold mb-2">E-mail</span></label>
                  <input 
                    type="email" 
                    dir="ltr"
                    className={`input input-bordered w-full bg-slate-50 focus:bg-white text-right ${errors.email ? 'input-error' : ''}`}
                    {...register('email')}
                  />
                  {errors.email && <span className="text-error text-xs mt-1">{errors.email.message}</span>}
                </div>

                {/* موضوع */}
                <div className="form-control">
                  <label className="label"><span className="label-text font-bold mb-2">موضوع پیام</span></label>
                  <select 
                    className={`select select-bordered w-full bg-slate-50 focus:bg-white ${errors.subject ? 'select-error' : ''}`}
                    {...register('subject')}
                  >
                    <option value="">انتخاب کنید...</option>
                    <option value="سفارش">پیگیری سفارش</option>
                    <option value="مشاوره">مشاوره قبل از چاپ</option>
                    <option value="مالی">امور مالی و پرداخت</option>
                    <option value="شکایت">انتقاد و شکایت</option>
                    <option value="سایر">سایر موارد</option>
                  </select>
                  {errors.subject && <span className="text-error text-xs mt-1">{errors.subject.message}</span>}
                </div>
              </div>

              {/* متن پیام */}
              <div className="form-control">
                <label className="label"><span className="label-text font-bold mb-2">متن پیام</span></label>
                <br/>
                <textarea 
                  className={`textarea textarea-bordered w-full h-32 bg-slate-50 focus:bg-white ${errors.message ? 'textarea-error' : ''}`}
                  placeholder={pageText.home.contactSection.placeHolderMessage}
                  {...register('message')}
                ></textarea>
                {errors.message && <span className="text-error text-xs mt-1">{errors.message.message}</span>}
              </div>

              {/* دکمه ارسال */}
              <div className="pt-2">
                <button 
                  type="submit" 
                  disabled={contactMutation.isPending}
                  className="btn btn-primary w-full md:w-auto px-8 text-lg font-bold shadow-lg shadow-primary/30"
                >
                  {contactMutation.isPending ? (
                    <>
                      <span className="loading loading-spinner"></span>
                     {pageText.home.contactSection.sending}
                    </>
                  ) : (
                    pageText.home.contactSection.sendMessage
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;