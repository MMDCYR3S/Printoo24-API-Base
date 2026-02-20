// src/app/pages/Home.jsx
import { useEffect } from "react";
import CategoryHero from "../features/home/CategoryHero";
import HomeSlider from "../features/home/HomeSlider"; 
import { ShieldCheck, Truck, Headset, FileCheck,Plus, Minus, HelpCircle, Phone, MapPin, Mail, Send, Instagram } from "lucide-react";
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
    // ... کدهای قبلی
    // فقط برای خلاصه شدن اینجا نیاوردم، شما دست نزنید بهشون
    const features = [
        {
          id: 1,
          icon: <FileCheck size={32} />,
          title: pageText.home.cards.id1.title,
          desc: pageText.home.cards.id1.value ,
          color: "bg-blue-50 text-blue-600 border-blue-100",
        },
        {
          id: 2,
          icon: <Truck size={32} />,
          title: pageText.home.cards.id2.title,
          desc: pageText.home.cards.id2.value,
          color: "bg-orange-50 text-orange-600 border-orange-100",
        },
        {
          id: 3,
          icon: <Headset size={32} />,
          title: pageText.home.cards.id3.title  ,
          desc: pageText.home.cards.id3.value ,
          color: "bg-emerald-50 text-emerald-600 border-emerald-100",
        },
        {
          id: 4,
          icon: <ShieldCheck size={32} />,
          title: pageText.home.cards.id4.title ,
          desc: pageText.home.cards.id4.value ,
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
      <div className="text-center mb-8">
        <h2 className="text-2xl md:text-3xl font-black text-slate-800 mb-2 flex items-center justify-center gap-2">
          <HelpCircle className="text-primary" />
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