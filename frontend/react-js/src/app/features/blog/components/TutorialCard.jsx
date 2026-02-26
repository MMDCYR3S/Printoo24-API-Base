import React from 'react';
import { Play, Calendar } from 'lucide-react';

const formatToJalali = (dateString) => {
  if (!dateString) return '';
  return new Intl.DateTimeFormat('fa-IR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(new Date(dateString));
};

const TutorialCard = ({ tutorial, onClick }) => {
  return (
    <div 
      onClick={() => onClick(tutorial.id)}
      className="group cursor-pointer bg-white rounded-2xl overflow-hidden border border-slate-100  hover:shadow-2xl hover:shadow-primary/10 transition-all duration-500 flex flex-col h-full"
    >
      {/* ── تصویر تامنیل و دکمه Play ── */}
      <div className="relative aspect-video overflow-hidden bg-slate-900 isolate">
        <img 
          src={tutorial.thumbnail} 
          alt={tutorial.title} 
          loading="lazy"
          className="w-full h-full object-cover opacity-90 group-hover:opacity-100  transition-all duration-700"
        />
        {/* افکت تاریکی روی عکس */}
        <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors duration-500 z-10" />

        {/* دکمه Play شیشه‌ای */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/40 group-hover:scale-110 group-hover:bg-primary group-hover:border-primary transition-all duration-500 shadow-xl z-20">
          <Play size={28} className="text-white " fill="currentColor" />
        </div>
      </div>

      {/* ── عنوان و تاریخ ── */}
      <div className="p-5 flex flex-col flex-1">
        <h3 className="text-lg font-black text-slate-800 line-clamp-2 group-hover:text-primary transition-colors mb-4">
          {tutorial.title}
        </h3>
        
        <div className="mt-auto flex items-center gap-2 text-xs font-medium text-slate-500 pt-4 border-t border-slate-100">
          <Calendar size={14} className="text-slate-400" />
          <span>{formatToJalali(tutorial.created_at)}</span>
        </div>
      </div>
    </div>
  );
};

export default TutorialCard;