// src/app/pages/Home.jsx
import { useEffect } from "react";
import CategoryHero from "../features/home/CategoryHero";
import HomeSlider from "../features/home/HomeSlider"; 
import { ShieldCheck, Truck, Headset, FileCheck,Plus, Minus, HelpCircle, Phone, MapPin, Mail, Send, Instagram } from "lucide-react";
import InfoModal from "../components/common/InfoModal";
import ContactSection from "../features/home/ContactSection"; 



import img501  from "../../assets/images/home/501.webp"
import img502 from "../../assets/images/home/502.webp"
import img503 from "../../assets/images/home/503.webp"
import img504 from "../../assets/images/home/504.webp"


const HomePage = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);



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

        <FAQSection />

<ContactSection />

      </div>
    </>
  );
};

const PageHelperPictures = ()=>{
  return(
    <>
    <div className="grid grid-cols-2 lg:grid-cols-4 items-center justify-center bg-white p-4 m-6 rounded-2xl shadow-sm">
      <a href="#"><img src={img501} alt="pages logo" className="hover:scale-105 duration-200"/></a>
      <img src={img502} alt="pages logo" className="hover:scale-105 duration-200"/>
      <img src={img503} alt="pages logo" className="hover:scale-105 duration-200"/>
      <img src={img504} alt="pages logo" className="hover:scale-105 duration-200"/>
    </div>
    </>
  )
}


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

        </>
      );

      
};

const FAQSection = () => {
  // دیتای استاتیک (بعداً می‌تونه از API بیاد)
  const faqs = [
    {
      question: "سفارش‌ها چند روزه به دستم می‌رسد؟",
      answer: "برای شهرهای سلیمانیه و اربیل معمولاً بین ۲۴ تا ۴۸ ساعت کاری زمان می‌برد. برای سایر شهرها بسته به باربری بین ۳ تا ۴ روز.",
    },
    {
      question: "آیا امکان پرداخت در محل وجود دارد؟",
      answer: "بله، برای مشتریان تأیید شده و همکاران قدیمی امکان تسویه در محل (COD) وجود دارد. همچنین می‌توانید از طریق FastPay پرداخت کنید.",
    },
    {
      question: "اگر چاپ کیفیت لازم را نداشت چه می‌شود؟",
      answer: "ما کیفیت را تضمین می‌کنیم. اگر ایراد از سمت ما (دستگاه یا متریال) باشد، بدون هیچ هزینه‌ای مجدداً چاپ و ارسال می‌شود.",
    },
    {
      question: "فایل‌ها را با چه فرمتی ارسال کنم؟",
      answer: "بهترین فرمت برای چاپ لارج فرمت TIFF با مد رنگی CMYK است. فایل‌های PDF و JPG با رزولوشن حداقل 72dpi هم پذیرفته می‌شوند.",
    },
  ];


  return (
    <section className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h2 className="text-2xl md:text-3xl font-black text-slate-800 mb-2 flex items-center justify-center gap-2">
          <HelpCircle className="text-primary" />
          سوالات متداول
        </h2>
        <p className="text-slate-500">پاسخ به پرسش‌هایی که شاید برای شما هم پیش بیاید</p>
      </div>

      <div className="grid gap-3 max-w-3xl mx-auto">
        {faqs.map((item, idx) => (
          <div 
            key={idx} 
            className="collapse collapse-plus bg-white border border-base-200 rounded-2xl shadow-sm hover:shadow-md transition-all duration-300"
          >
            <input type="radio" name="my-accordion-3" defaultChecked={idx === 0} /> 
            <div className="collapse-title text-lg font-bold text-slate-700">
              {item.question}
            </div>
            <div className="collapse-content">
              <p className="text-slate-600 leading-relaxed border-t border-base-100 pt-3">
                {item.answer}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};



export default HomePage;