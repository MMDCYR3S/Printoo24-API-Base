// src/app/features/home/HomePage.jsx
import { useEffect } from "react";
// import { Helmet } from 'react-helmet'; // برای سئو (اگر نصب نیست مهم نیست، کد کار میکند)
import CategoryHero from "../features/home/CategoryHero";
import { ShieldCheck, Truck, Headset, FileCheck } from "lucide-react";

const HomePage = () => {
  // اسکرول به بالا هنگام لود صفحه
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <>
      {/* 🟢 تنظیمات سئو صفحه اصلی */}
      {/* <Helmet> */}
      <title>Printoo24 | پنل تخصصی چاپ همکاران کردستان</title>
      <meta
        name="description"
        content="سامانه آنلاین سفارش چاپ بنر، کارت ویزیت و تراکت با تحویل فوری در سلیمانیه و اربیل."
      />
      {/* </Helmet> */}

      <div className="flex flex-col gap-12 pb-16">
        {/* 1. بخش هیرو (آکاردئون دسته‌ها و محصولات) */}
        {/* این همان کامپوننت پیچیده‌ای است که در مرحله قبل ساختیم */}
        <CategoryHero />

        {/* 2. بخش اعتماد سازی (Trust Indicators) */}
        {/* برای مشتری عراقی بسیار مهم است که بداند کالا چطور می‌رسد */}
        <TrustSection />

        {/* 3. بنر تبلیغاتی تکی (اختیاری - برای تنوع بصری) */}
        {/* <PromoBanner /> */}
      </div>
    </>
  );
};

// --- کامپوننت داخلی: بخش مزیت‌ها (Trust Section) ---
const TrustSection = () => {
  const features = [
    {
      id: 1,
      icon: <FileCheck size={32} />,
      title: "بررسی رایگان فایل",
      desc: "قبل از چاپ، فایل شما توسط طراح چک می‌شود تا خراب نشود.",
      color: "bg-blue-50 text-blue-600 border-blue-100",
    },
    {
      id: 2,
      icon: <Truck size={32} />,
      title: "ارسال مستقیم به عراق",
      desc: "تحویل در سلیمانیه و اربیل با باربری‌های معتبر و سریع.",
      color: "bg-orange-50 text-orange-600 border-orange-100",
    },
    {
      id: 3,
      icon: <Headset size={32} />,
      title: "پشتیبانی به زبان کوردی",
      desc: "پاسخگویی لحظه‌ای در واتساپ برای پیگیری سفارشات.",
      color: "bg-emerald-50 text-emerald-600 border-emerald-100",
    },
    {
      id: 4,
      icon: <ShieldCheck size={32} />,
      title: "ضمانت کیفیت چاپ",
      desc: "اگر چاپ مشکلی داشته باشد، با هزینه خودمان تجدید می‌کنیم.",
      color: "bg-purple-50 text-purple-600 border-purple-100",
    },
  ];

  // --- کامپوننت داخلی: بنر پروموشن (اختیاری) ---
  const PromoBanner = () => (
    <section className="container mx-auto px-4">
      <div className="relative rounded-3xl overflow-hidden bg-slate-800 h-[200px] md:h-[250px] shadow-xl flex items-center p-8 md:p-12">
        <div className="absolute inset-0 opacity-30">
          <img
            src="http://localhost:9010/media/categories/boxes/box_5121_1.jpg"
            className="w-full h-full object-cover grayscale"
            alt="Pattern"
          />
        </div>
        <div className="relative z-10 max-w-2xl">
          <div className="badge badge-warning font-bold mb-3">
            پیشنهاد ویژه همکاران
          </div>
          <h2 className="text-2xl md:text-4xl font-black text-white mb-2">
            تخفیف ۱۰٪ روی سفارش‌های لارج فرمت
          </h2>
          <p className="text-slate-300 mb-6">
            فقط تا پایان هفته جاری، برای سفارش‌های بالای ۱۰۰ متر مربع.
          </p>
        </div>
      </div>
    </section>
  );

  return (
    <>
      <section className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((item) => (
            <div
              key={item.id}
              className="flex flex-col items-center text-center p-6 rounded-2xl bg-white border border-base-200 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group"
            >
              <div
                className={`p-4 rounded-2xl mb-4 border ${item.color} group-hover:scale-110 transition-transform duration-300`}
              >
                {item.icon}
              </div>
              <h3 className="text-lg font-black text-base-content mb-2">
                {item.title}
              </h3>
              <p className="text-sm text-base-content/60 leading-relaxed font-medium">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      <PromoBanner />
    </>
  );
};

export default HomePage;
