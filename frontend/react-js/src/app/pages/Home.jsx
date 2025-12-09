// src/app/pages/Home.jsx
import { useEffect } from "react";
import CategoryHero from "../features/home/CategoryHero";
import HomeSlider from "../features/home/HomeSlider"; // <--- ایمپورت جدید
import { ShieldCheck, Truck, Headset, FileCheck } from "lucide-react";
import InfoModal from "../components/common/InfoModal";
import img501 from "../../assets/images/home/501.webp"
import img502 from "../../assets/images/home/502.webp"
import img503 from "../../assets/images/home/503.webp"
import img504 from "../../assets/images/home/504.webp"

const HomePage = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

const PageHelperPictures = ()=>{
  return(
    <>
    <div className="flex flex-row bg-white p-4 m-6 rounded-2xl shadow-sm">
      <img501 className="w-64 h-64" />

    </div>
    </>
  )
}


  return (
    <>
      <title>Printoo24 | پنل تخصصی چاپ همکاران کردستان</title>
      <meta
        name="description"
        content="سامانه آنلاین سفارش چاپ بنر، کارت ویزیت و تراکت با تحویل فوری در سلیمانیه و اربیل."
      />

      {/* کانتینر اصلی صفحه */}

      <InfoModal />


      <div className="flex flex-col gap-8 pb-16">

        <div className="mt-6"> 
           <HomeSlider />
        </div>

        {/* 2. بخش هیرو (آکاردئون دسته‌ها) */}
        <CategoryHero />

      <PageHelperPictures />



        {/* 3. بخش اعتماد سازی */}
        <TrustSection />

      </div>
    </>
  );
};

// ... بقیه کدهای TrustSection و PromoBanner بدون تغییر می‌مانند ...
// (فقط کد بالا را جایگزین بخش Return اصلی کنید)
// ...

const TrustSection = () => {
    // ... کدهای قبلی
    // فقط برای خلاصه شدن اینجا نیاوردم، شما دست نزنید بهشون
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
        <section className="container mx-auto px-4 my-6">
    
        </section>
    
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