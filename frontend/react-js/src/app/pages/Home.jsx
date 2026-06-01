// src/app/pages/Home.jsx
import React, { useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import {
  ShieldCheck,
  Truck,
  Headset,
  FileCheck,
  HelpCircle,
  MessageCircleQuestion,
  ChevronDown,
  ArrowUpLeft,
} from 'lucide-react';

import CategoryHero from '../features/home/CategoryHero';
import HomeSlider from '../features/home/HomeSlider';
import InfoModal from '../components/common/InfoModal';
import ContactSection from '../features/home/ContactSection';
import pageText from '../lang/pages.json';

import img501 from '../../assets/images/home/501.webp';

import img503 from '../../assets/images/home/503.webp';


/* ─────────────────────────────────────────────
   انیمیشن‌های مشترک
   ───────────────────────────────────────────── */
const staggerContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.05 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 200, damping: 24 },
  },
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.92 },
  show: {
    opacity: 1,
    scale: 1,
    transition: { type: 'spring', stiffness: 200, damping: 24 },
  },
};

/* ─── کامپوننت کمکی: محتوا با انیمیشن هنگام ورود به viewport ── */
const AnimatedSection = ({ children, className = '', delay = 0 }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-60px' });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.6, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

/* ═════════════════════════════════════════════
   صفحه اصلی
   ═════════════════════════════════════════════ */
const HomePage = () => {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <>
      <title>{pageText.home.title}</title>
      <meta name="description" content={pageText.home.fullTitle} />

      <InfoModal />

      <div className="flex flex-col pb-16">
        {/* 1. اسلایدر */}
        <div className="mt-6">
          <HomeSlider />
        </div>

        {/* 2. آکاردئون دسته‌ها */}
        <div className="mt-8">
          <CategoryHero />
        </div>

        {/* 3. تصاویر کمکی */}
        {/* <PageHelperPictures /> */}

        {/* 4. اعتمادسازی */}
        <TrustSection />

        {/* 5. سؤالات متداول */}
        <FAQSection />

        {/* 6. تماس */}
        {/* <ContactSection /> */}
      </div>
    </>
  );
};

/* ═════════════════════════════════════════════
   تصاویر کمکی (بنرها)
   ═════════════════════════════════════════════ */
// const PageHelperPictures = () => {
//   const ref = useRef(null);
//   const isInView = useInView(ref, { once: true, margin: '-40px' });

//   const images = [
//     { src: img501, alt: 'بنر ۱', link: '#' },

//     { src: img503, alt: 'بنر ۳' },

//   ];

//   return (
//     <motion.div
//       ref={ref}
//       variants={staggerContainer}
//       initial="hidden"
//       animate={isInView ? 'show' : 'hidden'}
//       className="container mx-auto px-4 my-6"
//     >
//       <div className="grid grid-cols-2 max-w-lg mx-auto gap-4">
//         {images.map((img, idx) => {
//           const Inner = (
//             <motion.div
//               variants={scaleIn}
//               className="
//                 relative rounded-2xl overflow-hidden
//                 ring-1 ring-black/[0.04]
//                 group cursor-pointer
//               "
//             >
//               <img
//                 src={img.src}
//                 alt={img.alt}
//                 loading="lazy"
//                 className="
//                   w-full h-full object-cover
//                   transition-transform duration-500 ease-out
//                   group-hover:scale-[1.04]
//                 "
//               />
//               <div className="
//                 absolute inset-0 bg-black/0 group-hover:bg-black/5
//                 transition-colors duration-300
//               " />
//             </motion.div>
//           );

//           return img.link ? (
//             <a key={idx} href={img.link}>
//               {Inner}
//             </a>
//           ) : (
//             <div key={idx}>{Inner}</div>
//           );
//         })}
//       </div>
//     </motion.div>
//   );
// };

/* ═════════════════════════════════════════════
   بخش اعتمادسازی
   ═════════════════════════════════════════════ */
const TrustSection = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-60px' });

  const features = [
    {
      id: 1,
      icon: FileCheck,
      title: pageText.home.cards.id1.title,
      desc: pageText.home.cards.id1.value,
      gradient: 'from-blue-500 to-indigo-600',
      lightBg: 'bg-blue-50',
      lightText: 'text-blue-600',
    },
    {
      id: 2,
      icon: Truck,
      title: pageText.home.cards.id2.title,
      desc: pageText.home.cards.id2.value,
      gradient: 'from-amber-500 to-orange-600',
      lightBg: 'bg-amber-50',
      lightText: 'text-amber-600',
    },
    {
      id: 3,
      icon: Headset,
      title: pageText.home.cards.id3.title,
      desc: pageText.home.cards.id3.value,
      gradient: 'from-emerald-500 to-teal-600',
      lightBg: 'bg-emerald-50',
      lightText: 'text-emerald-600',
    },
    {
      id: 4,
      icon: ShieldCheck,
      title: pageText.home.cards.id4.title,
      desc: pageText.home.cards.id4.value,
      gradient: 'from-violet-500 to-purple-600',
      lightBg: 'bg-violet-50',
      lightText: 'text-violet-600',
    },
  ];

  return (
    <section className="container mx-auto px-4 my-12">
      <motion.div
        ref={ref}
        variants={staggerContainer}
        initial="hidden"
        animate={isInView ? 'show' : 'hidden'}
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5"
      >
        {features.map((item) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={item.id}
              variants={fadeUp}
              className="
                group relative rounded-2xl
                bg-white
                ring-1 ring-black/[0.05]
                p-5 md:p-6
                transition-all duration-500 ease-out
                hover:-translate-y-1 hover:shadow-xl hover:shadow-black/[0.06]
                overflow-hidden
              "
            >
              {/* خط گرادیان بالا */}
              <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${item.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />

              {/* دایره تزئینی پس‌زمینه */}
              <div className={`
                absolute -bottom-8 -left-8 w-32 h-32 rounded-full
                bg-gradient-to-br ${item.gradient} opacity-[0.04]
                group-hover:opacity-[0.08] group-hover:scale-125
                transition-all duration-700
              `} />

              <div className="relative z-10 flex items-start gap-4">
                {/* آیکون */}
                <div className={`
                  shrink-0 w-12 h-12 rounded-xl
                  flex items-center justify-center
                  ${item.lightBg} ${item.lightText}
                  group-hover:bg-gradient-to-br group-hover:${item.gradient}
                  group-hover:text-white group-hover:shadow-lg
                  transition-all duration-500
                  group-hover:scale-105 group-hover:rotate-2
                `}>
                  <Icon size={24} strokeWidth={1.8} />
                </div>

                {/* متن */}
                <div className="flex-1 min-w-0">
                  <h3 className="text-base font-extrabold text-slate-800 mb-1.5 leading-tight">
                    {item.title}
                  </h3>
                  <p className="text-[13px] text-slate-500 leading-relaxed font-medium">
                    {item.desc}
                  </p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>
    </section>
  );
};

/* ═════════════════════════════════════════════
   سؤالات متداول
   ═════════════════════════════════════════════ */
const FAQItem = ({ item, index, isOpen, onToggle }) => {
  const contentRef = useRef(null);

  return (
    <motion.div
      variants={fadeUp}
      className={`
        rounded-2xl overflow-hidden
        transition-all duration-300
        ${isOpen
          ? 'bg-white ring-1 ring-primary/15 shadow-lg shadow-primary/5'
          : 'bg-white ring-1 ring-black/[0.05] hover:ring-black/[0.08] hover:shadow-sm'
        }
      `}
    >
      <button
        onClick={() => onToggle(index)}
        className="
          w-full flex items-center justify-between gap-4
          px-5 py-4 md:px-6 md:py-5
          text-right
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:rounded-2xl
          transition-colors duration-200
        "
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className={`
            shrink-0 w-8 h-8 rounded-lg
            flex items-center justify-center
            text-xs font-extrabold
            transition-all duration-300
            ${isOpen
              ? 'bg-primary text-white shadow-sm shadow-primary/20'
              : 'bg-slate-100 text-slate-400'
            }
          `}>
            {String(index + 1).padStart(2, '0')}
          </span>
          <h3 className={`
            text-[15px] md:text-base font-bold truncate
            transition-colors duration-200
            ${isOpen ? 'text-primary' : 'text-slate-700'}
          `}>
            {item.question}
          </h3>
        </div>

        <div className={`
          shrink-0 w-8 h-8 rounded-full
          flex items-center justify-center
          transition-all duration-300
          ${isOpen
            ? 'bg-primary/10 text-primary rotate-180'
            : 'bg-slate-100 text-slate-400'
          }
        `}>
          <ChevronDown size={16} strokeWidth={2.5} />
        </div>
      </button>

      <motion.div
        initial={false}
        animate={{
          height: isOpen ? 'auto' : 0,
          opacity: isOpen ? 1 : 0,
        }}
        transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
        className="overflow-hidden"
      >
        <div ref={contentRef} className="px-5 pb-5 md:px-6 md:pb-6 pr-16 md:pr-[72px]">
          <div className="border-t border-slate-100 pt-3">
            <p className="text-[13px] md:text-sm text-slate-500 leading-[1.8] font-medium">
              {item.answer}
            </p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

const FAQSection = () => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-60px' });
  const [openIndex, setOpenIndex] = React.useState(0);

  const faqs = [
    {
      question: pageText.home.faq.question1.title ,
      answer: pageText.home.faq.question1.value,
    },
    {
      question: pageText.home.faq.question2.title,
      answer: pageText.home.faq.question2.value,
    },
    {
      question: pageText.home.faq.question3.title,
      answer: pageText.home.faq.question3.value,
    },
    {
      question: pageText.home.faq.question4.title,
      answer: pageText.home.faq.question4.value,
    },
  ];

  const handleToggle = (idx) => {
    setOpenIndex((prev) => (prev === idx ? -1 : idx));
  };

  return (
    <section className="container mx-auto px-4 py-12">
      {/* هدر */}
      <AnimatedSection className="text-center mb-10">
        <div className="inline-flex items-center gap-2 bg-primary/8 text-primary px-4 py-1.5 rounded-full text-xs font-bold mb-4">
          <MessageCircleQuestion size={14} />
          پرسیارە باوەکان 
        </div>
        <h2 className="text-2xl md:text-3xl font-extrabold text-slate-800">
          {pageText.home.faqTitle}
        </h2>
      </AnimatedSection>

      {/* لیست سؤالات */}
      <motion.div
        ref={ref}
        variants={staggerContainer}
        initial="hidden"
        animate={isInView ? 'show' : 'hidden'}
        className="max-w-3xl mx-auto flex flex-col gap-3"
      >
        {faqs.map((item, idx) => (
          <FAQItem
            key={idx}
            item={item}
            index={idx}
            isOpen={openIndex === idx}
            onToggle={handleToggle}
          />
        ))}
      </motion.div>
    </section>
  );
};

export default HomePage;