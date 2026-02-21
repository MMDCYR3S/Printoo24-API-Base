// src/app/pages/Home.jsx
import { useEffect } from "react";
import CategoryHero from "../features/home/CategoryHero";
import HomeSlider from "../features/home/HomeSlider"; 
import { ShieldCheck, Truck, Headset, FileCheck,Plus, Minus, HelpCircle, Phone, MapPin, Mail, Send, Instagram ,  } from "lucide-react";
import InfoModal from "../components/common/InfoModal";
import ContactSection from "../features/home/ContactSection"; 
import pageText from '../lang/pages.json'


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
      <title>{pageText.home.title}</title>
      <meta
        name="description"
        content= {pageText.home.fullTitle}
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
    <div className="grid grid-cols-2 lg:grid-cols-4 items-center justify-center bg-base p-4 m-6 ">
      <a href="#"><img src={img501} alt="pages logo" className="hover:scale-105 duration-200"/></a>
      <img src={img502} alt="pages logo" className="hover:scale-105 duration-200"/>
      <img src={img503} alt="pages logo" className="hover:scale-105 duration-200"/>
      <img src={img504} alt="pages logo" className="hover:scale-105 duration-200"/>
    </div>
    </>
  )
}

const TrustSection = () => {
  // برای تست، من مقادیر متنی را هاردکد کردم. شما می‌توانید از pageText خودتان استفاده کنید.
const features = [
    {
      id: 1,
      icon: <FileCheck size={28} />, 
      title: pageText.home.cards.id1.title,
      desc: pageText.home.cards.id1.value,
      colorClasses: {
        bg: "bg-blue-100/80",
        text: "text-blue-600",
      },
    },
    {
      id: 2,
      icon: <Truck size={28} />,
      title: pageText.home.cards.id2.title,
      desc: pageText.home.cards.id2.value,
      colorClasses: {
        bg: "bg-orange-100/80",
        text: "text-orange-600",
      },
    },
    {
      id: 3,
      icon: <Headset size={28} />,
      title: pageText.home.cards.id3.title,
      desc: pageText.home.cards.id3.value,
      colorClasses: {
        bg: "bg-emerald-100/80",
        text: "text-emerald-600",
      },
    },
    {
      id: 4,
      icon: <ShieldCheck size={28} />,
      title: pageText.home.cards.id4.title,
      desc: pageText.home.cards.id4.value,
      colorClasses: {
        bg: "bg-purple-100/80",
        text: "text-purple-600",
      },
    },
  ];

  return (
    <section className="container mx-auto px-4 my-12">
      {/* نکته مهم برای زبان فارسی:
         فرض بر این است که کل پروژه شما دارای dir="rtl" است.
         در این صورت، وقتی از flex استفاده می‌کنیم، اولین فرزند در سمت راست قرار می‌گیرد.
         بنابراین ترتیب کد نویسی ما به شکل [ظرف متن] و سپس [ظرف آیکون] خواهد بود.
      */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((item) => (
          <div
            key={item.id}
            className="
              group relative overflow-hidden rounded-[35px] border border-base-200/50 bg-base-100 p-6 shadow-sm transition-all duration-500 ease-out
              /* استایل هاور کارت اصلی */
              hover:-translate-y-2 hover:shadow-2xl
              /* --- انیمیشن پر شدن رنگ اصلی --- */
              /* ایجاد یک لایه مخفی که در هاور بزرگ می‌شود */
              before:absolute before:inset-0 before:z-0 before:h-full before:w-full before:origin-bottom-right before:scale-0 before:rounded-[40px] before:rounded-br-[0px] before:bg-primary before:transition-transform before:duration-500 before:ease-out
              /* در حالت هاور، سایز این لایه بزرگ می‌شود تا کل کارت را بگیرد */
              hover:before:scale-[2.5]
            "
          >
            {/* نگهدارنده محتوا با z-index بالاتر برای قرار گرفتن روی لایه رنگی */}
            <div className="relative z-10 flex items-center justify-between gap-4">

              <div
                // در حالت عادی از رنگ‌های تعریف شده در آرایه استفاده می‌کند
                // در حالت هاور، پس زمینه سفید می‌شود و آیکون به رنگ اصلی در می‌آید تا داخل کادر رنگی دیده شود
                className={`
                  p-4 rounded-2xl transition-all duration-500 group-hover:scale-110 group-hover:rotate-3 shadow-sm
                  ${item.colorClasses.bg} ${item.colorClasses.text}
                  group-hover:bg-white group-hover:text-primary group-hover:shadow-md
                `}
              >
                {item.icon}
              </div>

              
              {/* بخش متن‌ها (سمت راست در RTL) */}
              <div className="flex flex-col items-start text-right transition-colors duration-300 group-hover:text-primary-content">
                <h3 className="text-xl font-black mb-2">
                  {item.title}
                </h3>
                <p className="text-sm font-medium opacity-70 leading-relaxed group-hover:opacity-90">
                  {item.desc}
                </p>
              </div>

              {/* بخش آیکون (سمت چپ در RTL) */}


            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
  
const FAQSection = () => {
  // دیتای استاتیک (بعداً می‌تونه از API بیاد)
  const faqs = [
    {
      question: pageText.home.faq.question1.title,
      answer: pageText.home.faq.question1.value ,
    },
    {
      question:  pageText.home.faq.question2.title,
      answer: pageText.home.faq.question2.value ,
    },
    {
      question: pageText.home.faq.question3.title ,
      answer: pageText.home.faq.question3.value ,
    },
    {
      question: pageText.home.faq.question4.title ,
      answer: pageText.home.faq.question4.value ,
    },
  ];


  return (
    <section className="container mx-auto px-4 py-8">
<div className="text-center mb-10">
        <h2 className="text-3xl md:text-4xl font-black text-base-content flex items-center justify-center gap-3">
          <HelpCircle size={36} className="text-primary" />
          {pageText.home.faqTitle}
        </h2>
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