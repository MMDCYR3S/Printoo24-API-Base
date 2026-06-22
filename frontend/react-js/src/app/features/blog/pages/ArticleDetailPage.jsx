import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Calendar,
  Clock,
  Eye,
  User,
  Tag,
  ChevronRight,
  AlertCircle,
  Share2,
  Copy,
  Check,
  ArrowUp,
  BookOpen,
} from 'lucide-react';
import SEO from '../../../components/common/SEO';
import ProductCard from '../../../components/product/ProductCard';
import { useArticleDetail } from '../hooks/useArticleDetail';

/* ─── هلپرها ─── */
const parseTags = (tagsString) => {
  if (!tagsString) return [];
  return tagsString
    .split(/,|،/)
    .map((t) => t.trim())
    .filter(Boolean);
};

const formatToJalali = (dateString) => {
  if (!dateString) return '';
  return new Intl.DateTimeFormat('EN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(dateString));
};

/* ─── انیمیشن‌های CSS به صورت inline (inject once) ─── */
const injectStyles = () => {
  const id = 'article-detail-animations';
  if (document.getElementById(id)) return;
  const style = document.createElement('style');
  style.id = id;
  style.textContent = `
    /* نوار پیشرفت خواندن */
    .reading-progress-bar {
      position: fixed;
      top: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, var(--color-primary, #6366f1) 0%, #a78bfa 100%);
      z-index: 9999;
      transition: width 80ms linear;
      border-radius: 0 0 0 2px;
    }

    /* انیمیشن fade-in-up */
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(24px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .anim-fade-in-up {
      animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    .anim-delay-1 { animation-delay: 0.08s; }
    .anim-delay-2 { animation-delay: 0.16s; }
    .anim-delay-3 { animation-delay: 0.24s; }
    .anim-delay-4 { animation-delay: 0.32s; }

    /* انیمیشن اسکلتون لودینگ بهتر */
    @keyframes shimmer {
      0%   { background-position: -400px 0; }
      100% { background-position: 400px 0; }
    }
    .skeleton-shimmer {
      background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 37%, #e2e8f0 63%);
      background-size: 800px 100%;
      animation: shimmer 1.6s ease-in-out infinite;
    }

    /* دکمه بازگشت به بالا */
    .scroll-to-top {
      transition: opacity 0.3s, transform 0.3s;
    }
    .scroll-to-top.hidden {
      opacity: 0;
      transform: translateY(16px);
      pointer-events: none;
    }
    .scroll-to-top.visible {
      opacity: 1;
      transform: translateY(0);
    }

    /* هاور تگ‌ها */
    .tag-chip {
      transition: all 0.2s cubic-bezier(0.22, 1, 0.36, 1);
    }
    .tag-chip:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }

    /* بهبود تایپوگرافی محتوای HTML */
    .article-body > p        { margin-bottom: 1.5rem; font-size: 1.05rem; line-height: 2.1; }
    .article-body > h1       { font-size: 1.85rem; font-weight: 900; color: #1e293b; margin: 3rem 0 1.25rem; }
    .article-body > h2       { font-size: 1.55rem; font-weight: 800; color: #334155; margin: 2.5rem 0 1rem; }
    .article-body > h3       { font-size: 1.25rem; font-weight: 700; color: #334155; margin: 2rem 0 0.75rem; }
    .article-body > ul,
    .article-body > ol       { margin: 0 2rem 1.5rem 0; }
    .article-body > ul       { list-style: disc; }
    .article-body > ol       { list-style: decimal; }
    .article-body li         { margin-bottom: 0.6rem; line-height: 2; }
    .article-body img        { border-radius: 1rem; margin: 2.5rem 0; width: 100%; object-fit: cover; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
    .article-body a          { color: var(--color-primary, #6366f1); text-decoration: underline; text-underline-offset: 3px; font-weight: 600; }
    .article-body blockquote {
      border-right: 4px solid #cbd5e1;
      padding: 1rem 1.5rem;
      margin: 2rem 0;
      background: #f8fafc;
      border-radius: 0 0.75rem 0.75rem 0;
      color: #64748b;
      font-style: italic;
    }
    .article-body pre {
      background: #1e293b;
      color: #e2e8f0;
      padding: 1.25rem;
      border-radius: 0.75rem;
      overflow-x: auto;
      margin: 1.5rem 0;
      font-size: 0.9rem;
      line-height: 1.7;
    }
    .article-body code {
      background: #f1f5f9;
      padding: 0.15rem 0.4rem;
      border-radius: 0.3rem;
      font-size: 0.9em;
    }
    .article-body pre code {
      background: transparent;
      padding: 0;
    }
    .article-body table {
      width: 100%;
      border-collapse: collapse;
      margin: 1.5rem 0;
    }
    .article-body th, .article-body td {
      border: 1px solid #e2e8f0;
      padding: 0.75rem 1rem;
      text-align: right;
    }
    .article-body th {
      background: #f8fafc;
      font-weight: 700;
    }

    @media (min-width: 768px) {
      .article-body > p { font-size: 1.125rem; }
    }
  `;
  document.head.appendChild(style);
};

/* ─── کامپوننت لودینگ اسکلتون بهبود یافته ─── */
const ArticleSkeleton = () => (
  <div className="container mx-auto px-4 py-12 max-w-5xl" dir="rtl">
    {/* Breadcrumb skeleton */}
    <div className="skeleton-shimmer h-5 rounded-lg w-32 mb-8" />

    {/* Hero image skeleton */}
    <div className="skeleton-shimmer aspect-video md:aspect-[21/9] rounded-3xl mb-8" />

    {/* Title skeleton */}
    <div className="bg-white rounded-3xl p-8 shadow-sm mb-8 -mt-16 relative z-10 mx-4 md:mx-12">
      <div className="skeleton-shimmer h-6 rounded-full w-24 mb-6" />
      <div className="skeleton-shimmer h-10 rounded-xl w-4/5 mb-4" />
      <div className="skeleton-shimmer h-10 rounded-xl w-3/5 mb-8" />
      <div className="flex gap-6 pt-6 border-t border-slate-100">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="skeleton-shimmer h-5 rounded-lg w-24" />
        ))}
      </div>
    </div>

    {/* Content skeleton */}
    <div className="bg-white rounded-3xl p-8 md:p-12 shadow-sm space-y-5">
      {[100, 100, 85, 100, 90, 75, 100, 60].map((w, i) => (
        <div key={i} className="skeleton-shimmer h-4 rounded-lg" style={{ width: `${w}%` }} />
      ))}
    </div>
  </div>
);

/* ─── کامپوننت خطا بهبود یافته ─── */
const ArticleError = ({ error }) => (
  <div className="min-h-[60vh] flex items-center justify-center px-4" dir="rtl">
    <div className="text-center max-w-md anim-fade-in-up">
      <div className="w-20 h-20 mx-auto mb-6 bg-red-50 rounded-full flex items-center justify-center">
        <AlertCircle size={36} className="text-red-400" />
      </div>
      <h2 className="text-2xl font-extrabold text-slate-800 mb-3">بابەت نەدۆزرایەوە</h2>
      <p className="text-slate-500 mb-8 leading-relaxed">
        {error || 'لەوانەیە ناونیشانەکەت هەڵە بێت یان بابەتەکە سڕدرابێتەوە'}
      </p>
      <Link
        to="/blog"
        className="inline-flex items-center gap-2 px-7 py-3.5 bg-primary text-white rounded-2xl font-bold hover:bg-primary/90 transition-all shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/25 hover:-translate-y-0.5"
      >
        <ChevronRight size={18} />
        بڵاگەکان
      </Link>
    </div>
  </div>
);

/* ─── کامپوننت اشتراک‌گذاری ─── */
const ShareButton = ({ title, url }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(url || window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* fallback silent */
    }
  }, [url]);

  const handleNativeShare = useCallback(async () => {
    if (navigator.share) {
      try {
        await navigator.share({ title, url: url || window.location.href });
      } catch {
        /* user cancelled */
      }
    } else {
      handleCopy();
    }
  }, [title, url, handleCopy]);

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleNativeShare}
        className="flex items-center gap-2 px-4 py-2  text-secondary bg-primary/30 hover:bg-primary/50 rounded-xl text-sm font-medium transition-all hover:-translate-y-0.5 hover:shadow-sm"
        title="هاوبەشکردن"
      >
        <Share2 size={16} />
        <span className="hidden sm:inline">هاوبەشکردن</span>
      </button>
      <button
        onClick={handleCopy}
        className="flex items-center gap-2 px-4 py-2 text-secondary bg-primary/30 hover:bg-primary/50  rounded-xl text-sm font-medium transition-all hover:-translate-y-0.5 hover:shadow-sm"
        title="کپی  کۆپیکردنی بەستەر"
      >
        {copied ? <Check size={16} className="text-emerald-500" /> : <Copy size={16} />}
        <span className="hidden sm:inline">{copied ? 'کۆپی کرا' : ' کۆپیکردنی بەستەر'}</span>
      </button>
    </div>
  );
};

/* ═══════════════════════════════════════════
   کامپوننت اصلی صفحه جزئیات مقاله
   ═══════════════════════════════════════════ */
const ArticleDetailPage = () => {
  const { id } = useParams();
  const { article, isLoading, error } = useArticleDetail(id);

  const articleRef = useRef(null);
  const [readingProgress, setReadingProgress] = useState(0);
  const [showScrollTop, setShowScrollTop] = useState(false);

  /* inject animations once */
  useEffect(() => {
    injectStyles();
  }, []);

  /* نوار پیشرفت خواندن + دکمه بازگشت به بالا */
  useEffect(() => {
    if (!article) return;

    const handleScroll = () => {
      const el = articleRef.current;
      if (!el) return;

      const rect = el.getBoundingClientRect();
      const totalHeight = el.scrollHeight;
      const scrolled = Math.max(0, -rect.top);
      const progress = Math.min(100, (scrolled / (totalHeight - window.innerHeight)) * 100);
      setReadingProgress(progress);
      setShowScrollTop(window.scrollY > 600);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [article]);

  const scrollToTop = useCallback(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  /* ─── حالت لودینگ ─── */
  if (isLoading) return <ArticleSkeleton />;

  /* ─── حالت خطا ─── */
  if (error || !article) return <ArticleError error={error} />;

  const tagsList = parseTags(article.tags);

  return (
    <div className="bg-slate-50/60 min-h-screen pb-20" dir="rtl" ref={articleRef}>
      {/* نوار پیشرفت خواندن */}
      <div className="reading-progress-bar" style={{ width: `${readingProgress}%` }} />

      {/* سئو */}
      <SEO
        title={article.meta_title || article.title}
        description={article.meta_description || article.summary}
        keywords={article.tags}
        ogImage={article.image}
        type="article"
      />

      {/* ── Breadcrumb ── */}
      <nav className="container mx-auto px-4 py-6 max-w-5xl anim-fade-in-up" aria-label="Breadcrumb">
        <Link
          to="/blog"
          className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-primary transition-colors font-medium group"
        >
          <ChevronRight size={16} className="transition-transform group-hover:translate-x-[-3px]" />
          بڵاگەکان
        </Link>
      </nav>

      <article className="container mx-auto px-4 max-w-5xl">
        {/* ── Hero Section ── */}
        <div className="relative mb-36 md:mb-28 mt-2 anim-fade-in-up anim-delay-1">
          {/* تصویر اصلی */}
          <div className="relative aspect-[16/9]  rounded-3xl overflow-hidden  border border-slate-100/80">
            <img
              src={article.image}
              alt={article.title}
              className="w-full h-full object-cover"
              loading="eager"
            />
            <div className="absolute inset-0  to-transparent" />
          </div>

          {/* Overlap Card */}

        </div>
                  <div className=" -mt-52 mb-20 mx-8 left-3 right-3 md:left-10 md:right-10 bg-radial from-white/50 to-slate-200/80 backdrop-blur-md rounded-3xl md:rounded-[3rem] border-t border-t-white border-r border-r-slate-300 border-l border-l-slate-300 p-4 md:p-8 anim-fade-in-up anim-delay-2">
            {/* دسته‌بندی + اشتراک‌گذاری */}
            <div className="flex items-center justify-between ">
              <span className="px-4  bg-primary/10 text-primary text-xs font-bold rounded-full">
                {article.category_name}
              </span>
              <ShareButton title={article.title} />
            </div>

            <h1 className="text-2xl md:text-[2.25rem] font-black text-slate-800 mb-6 leading-[1.4] md:leading-[1.35]">
              {article.title}
            </h1>

            {/* متادیتا */}
            <div className="flex flex-wrap items-center gap-4 md:gap-6 text-xs md:text-sm text-slate-500 font-medium  ">
              <div className="flex items-center gap-2">

              </div>

              <div className="flex items-center gap-1.5 text-primary">
                <Calendar size={16} />
                <span>{new Intl.DateTimeFormat('en-US', { year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(article.published_at))}</span>
              </div>



            </div>
          </div>

        {/* ── محتوای اصلی ── */}
        <div className="bg-white rounded-3xl p-6 md:p-12 shadow-sm border border-slate-100/80 mb-12 anim-fade-in-up anim-delay-3">
          {/* چکیده */}
          {article.summary && (
            <div className="bg-gradient-to-l from-primary/[0.04] to-primary/[0.08] border-r-4 border-primary p-6 rounded-l-2xl mb-10">
              <p className="text-base md:text-lg font-medium text-slate-700 leading-relaxed">
                {article.summary}
              </p>
            </div>
          )}

          {/* محتوای HTML */}
          <div
            className="article-body text-slate-700 text-justify font-medium"
            dangerouslySetInnerHTML={{ __html: article.content }}
          />

          {/* تگ‌ها */}
          {tagsList.length > 0 && (
            <div className="mt-16 pt-8 border-t border-slate-100 flex flex-wrap items-center gap-2.5">
              <Tag size={18} className="text-slate-400 ml-1" />
              {tagsList.map((tag, index) => (
                <span
                  key={index}
                  className="tag-chip px-4 py-2 bg-slate-50 border border-slate-200 text-slate-600 rounded-xl text-sm font-medium hover:bg-primary/5 hover:text-primary hover:border-primary/20 cursor-pointer"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* ── محصولات مرتبط ── */}
        {article.related_products?.length > 0 && (
          <div className="mb-12 anim-fade-in-up anim-delay-4">
            <h3 className="text-2xl font-extrabold text-slate-800 mb-8 flex items-center gap-3">
              <span className="w-1.5 h-8 bg-primary rounded-full" />
              بەرهەمە پەیوەندیدارەکان بە ئەم بابەتە
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {article.related_products.map((rp) => (
                <ProductCard
                  key={rp.id}
                  product={{
                    ...rp,
                    thumbnail: rp.thumbnail,
                    category: { parent_category: ' بەرهەمە پەیوەندیدارەکان بە ئەم بابەتە' },
                    has_price: rp.has_price,
                  }}
                />
              ))}
            </div>
          </div>
        )}
      </article>

      {/* ── دکمه بازگشت به بالا ── */}
      <button
        onClick={scrollToTop}
        aria-label=" گەڕانەوە بۆ سەرەوە"
        className={`scroll-to-top fixed bottom-6 left-6 z-50 w-12 h-12 bg-white border border-slate-200 rounded-2xl shadow-lg flex items-center justify-center text-slate-500 hover:text-primary hover:border-primary/30 hover:shadow-xl ${
          showScrollTop ? 'visible' : 'hidden'
        }`}
      >
        <ArrowUp size={20} />
      </button>
    </div>
  );
};

export default ArticleDetailPage;