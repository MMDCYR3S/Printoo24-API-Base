import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, User, Calendar } from 'lucide-react';

const ArticleCard = ({ article }) => {
  // فرمت تاریخ میلادی (Gregorian)
  const formattedDate = new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(new Date(article.published_at));

  return (
    <article className="group bg-white rounded-2xl overflow-hidden border border-slate-100  hover:shadow-xl transition-all duration-300 flex flex-col h-full">
      {/* تصویر مقاله با نسبت 16:9 */}
      <Link to={`/blog/${article.id}`} className="relative aspect-[16/9] overflow-hidden block">
        <img
          src={article.image}
          alt={article.title}
          loading="lazy"
          className="w-full h-full object-cover transform  transition-transform duration-500"
        />
        <div className="absolute top-3 right-3 bg-white/60 backdrop-blur-sm px-3 py-1 rounded-md text-xs font-semibold text-primary shadow-sm">
          {article.category_name}
        </div>
      </Link>

      {/* محتوای مقاله */}
      <div className="p-5 flex flex-col flex-1">
        <Link to={`/blog/${article.id}`}>
          <h3 className="text-xl font-bold text-primary mb-3 line-clamp-2 group-hover:text-primary transition-colors">
            {article.title}
          </h3>
        </Link>
        
        <p className="text-slate-500 text-sm mb-5 line-clamp-3 leading-relaxed flex-1">
          {article.summary}
        </p>

        {/* متادیتا (نویسنده، تاریخ، زمان مطالعه) */}
        <div className="pt-4 border-t border-slate-100 flex flex-wrap items-center gap-3 text-xs text-slate-500">

          
          <div className="flex items-center justify-between w-full gap-3">
            <div className="flex items-center gap-1">
              <Calendar size={14} className="text-slate-400" />
              <span>{formattedDate}</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock size={14} className="text-slate-400 -mt-1" />
              <span dir='ltr'>{article.read_time}  min</span>
            </div>
          </div>
        </div>
      </div>
    </article>
  );
};

export default ArticleCard;