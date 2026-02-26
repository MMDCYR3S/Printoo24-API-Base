import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { Calendar, Clock, Eye, User, Tag, ChevronRight, AlertCircle } from 'lucide-react';
import SEO from '../../../components/common/SEO';
import ProductCard from '../../../components/product/ProductCard';
import { useArticleDetail } from '../hooks/useArticleDetail';

// هلپر برای تبدیل تگ‌های استرینگ به آرایه (پشتیبانی از کامای فارسی و انگلیسی)
const parseTags = (tagsString) => {
  if (!tagsString) return [];
  return tagsString.split(/,|،/).map(t => t.trim()).filter(Boolean);
};

// هلپر برای تبدیل تاریخ میلادی به شمسی
const formatToJalali = (dateString) => {
  if (!dateString) return '';
  return new Intl.DateTimeFormat('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(new Date(dateString));
};

const ArticleDetailPage = () => {
  // اگر تو روت از :id یا :id استفاده کردی، همونو اینجا بگیر
  const { id } = useParams(); 
  const { article, isLoading, error } = useArticleDetail(id);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12 max-w-4xl animate-pulse">
        <div className="h-8 bg-slate-200 rounded w-1/4 mb-8"></div>
        <div className="aspect-[21/9] bg-slate-200 rounded-3xl mb-8"></div>
        <div className="h-12 bg-slate-200 rounded w-3/4 mb-8"></div>
        <div className="space-y-4">
          <div className="h-4 bg-slate-200 rounded w-full"></div>
          <div className="h-4 bg-slate-200 rounded w-full"></div>
          <div className="h-4 bg-slate-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="container mx-auto px-4 py-20 flex flex-col items-center justify-center text-center">
        <AlertCircle size={64} className="text-red-400 mb-4" />
        <h2 className="text-2xl font-bold text-slate-800 mb-2">مقاله یافت نشد!</h2>
        <p className="text-slate-500 mb-6">{error || 'ممکن است آدرس را اشتباه وارد کرده باشید یا مقاله حذف شده باشد.'}</p>
        <Link to="/blog" className="px-6 py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-all">
          بازگشت به بلاگ
        </Link>
      </div>
    );
  }

  const tagsList = parseTags(article.tags);

  return (
    <div className="bg-slate-50/50 min-h-screen pb-20" dir="rtl">
      {/* ── تنظیمات سئوی داینامیک ── */}
      <SEO 
        title={article.meta_title || article.title} 
        description={article.meta_description || article.summary}
        keywords={article.tags}
        ogImage={article.image}
        type="article"
      />

      {/* ── نوار ناوبری (Breadcrumb) ── */}
      <div className="container mx-auto px-4 py-6 max-w-5xl">
        <Link to="/blog" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-primary transition-colors font-medium">
          <ChevronRight size={16} />
          بازگشت به مقالات
        </Link>
      </div>

      <article className="container mx-auto px-4 max-w-5xl">
        
        {/* ── Hero Section (Overlapping Design) ── */}
        <div className="relative mb-32 md:mb-24 mt-4">
          {/* تصویر اصلی */}
          <div className="relative aspect-video md:aspect-[21/9] rounded-3xl overflow-hidden shadow-lg border border-slate-100">
            <img 
              src={article.image} 
              alt={article.title} 
              className="w-full h-full object-cover"
            />
            {/* گرادیانت تیره برای خوانایی بهتر اگر متنی روی عکس بیاد */}
            <div className="absolute inset-0 bg-gradient-to-t from-slate-900/40 to-transparent"></div>
          </div>

          {/* باکس اطلاعات هم‌پوشانی شده (Overlap Card) */}
          <div className="absolute -bottom-24 md:-bottom-12 left-4 right-4 md:left-12 md:right-12 bg-white/95 backdrop-blur-xl rounded-2xl md:rounded-3xl p-6 md:p-8 shadow-2xl shadow-slate-200/50 border border-white">
            <div className="flex items-center gap-3 mb-4">
              <span className="px-4 py-1.5 bg-primary/10 text-primary text-xs font-bold rounded-full">
                {article.category_name}
              </span>
            </div>
            
            <h1 className="text-2xl md:text-4xl font-black text-slate-800 mb-6 leading-tight">
              {article.title}
            </h1>

            <div className="flex flex-wrap items-center gap-4 md:gap-8 text-xs md:text-sm text-slate-500 font-medium border-t border-slate-100 pt-6">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
                  <User size={16} />
                </div>
                <span className="text-slate-700">{article.author_name}</span>
              </div>
              
              <div className="flex items-center gap-2">
                <Calendar size={18} className="text-slate-400" />
                <span>{formatToJalali(article.published_at)}</span>
              </div>

              <div className="flex items-center gap-2">
                <Clock size={18} className="text-slate-400" />
                <span>{article.read_time} دقیقه مطالعه</span>
              </div>

              <div className="flex items-center gap-2">
                <Eye size={18} className="text-slate-400" />
                <span>{article.views_count} بازدید</span>
              </div>
            </div>
          </div>
        </div>

        {/* ── محتوای اصلی مقاله (Typography & Content) ── */}
        <div className="bg-white rounded-3xl p-6 md:p-12 shadow-sm border border-slate-100 mb-12">
          
          {/* چکیده (Summary) */}
          {article.summary && (
            <div className="bg-primary/5 border-r-4 border-primary p-6 rounded-l-2xl mb-10">
              <p className="text-lg font-medium text-slate-700 leading-relaxed">
                {article.summary}
              </p>
            </div>
          )}

          {/* محتوای HTML با استایل‌های تایپوگرافی تزریق شده */}
          <div 
            className="
              text-slate-700 leading-[2.2] text-justify font-medium
              [&>p]:mb-6 [&>p]:text-base md:[&>p]:text-lg
              [&>h1]:text-3xl [&>h1]:font-black [&>h1]:text-slate-900 [&>h1]:mb-6 [&>h1]:mt-12
              [&>h2]:text-2xl [&>h2]:font-black [&>h2]:text-slate-800 [&>h2]:mb-5 [&>h2]:mt-10
              [&>h3]:text-xl [&>h3]:font-bold [&>h3]:text-slate-800 [&>h3]:mb-4 [&>h3]:mt-8
              [&>ul]:list-disc [&>ul]:mr-8 [&>ul]:mb-6 [&>ul]:marker:text-primary
              [&>ol]:list-decimal [&>ol]:mr-8 [&>ol]:mb-6 [&>ol]:marker:text-primary [&>ol]:marker:font-bold
              [&>li]:mb-3
              [&>img]:rounded-2xl [&>img]:shadow-md [&>img]:my-10 [&>img]:w-full [&>img]:object-cover
              [&>a]:text-primary [&>a]:underline [&>a]:font-bold [&>a]:underline-offset-4
              [&>blockquote]:border-r-4 [&>blockquote]:border-slate-300 [&>blockquote]:pr-6 [&>blockquote]:italic [&>blockquote]:text-slate-500 [&>blockquote]:my-8 [&>blockquote]:bg-slate-50 [&>blockquote]:py-4 [&>blockquote]:rounded-l-xl
            "
            dangerouslySetInnerHTML={{ __html: article.content }}
          />

          {/* ── تگ‌ها (Tags) ── */}
          {tagsList.length > 0 && (
            <div className="mt-16 pt-8 border-t border-slate-100 flex flex-wrap items-center gap-3">
              <Tag size={20} className="text-slate-400 ml-2" />
              {tagsList.map((tag, index) => (
                <span 
                  key={index}
                  className="px-4 py-2 bg-slate-50 border border-slate-200 text-slate-600 rounded-xl text-sm font-medium hover:bg-slate-100 hover:text-primary transition-colors cursor-pointer"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* ── محصولات مرتبط ── */}
        {article.related_products && article.related_products.length > 0 && (
          <div className="mb-12">
            <h3 className="text-2xl font-black text-slate-800 mb-8 border-b border-slate-200 pb-4">
              محصولات مرتبط با این مقاله
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {article.related_products.map((rp) => {
                // آداپتور: تبدیل دیتای محصول مرتبط بلاگ به فرمت قابل فهم برای ProductCard
                const mappedProduct = {
                  ...rp,
                  thumbnail: rp.image, // ProductCard از thumbnail استفاده میکنه
                  category: { parent_category: 'محصول مرتبط' }, 
                  has_price: false // چون API بلاگ قیمت نمیده، دکمه تماس رو فعال میکنیم
                };
                
                return (
                  <ProductCard key={rp.id} product={mappedProduct} />
                );
              })}
            </div>
          </div>
        )}

      </article>
    </div>
  );
};

export default ArticleDetailPage;