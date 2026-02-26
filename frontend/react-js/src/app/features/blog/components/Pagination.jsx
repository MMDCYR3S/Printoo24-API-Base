import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const Pagination = ({ currentPage, onPageChange, hasMore }) => {
  return (
    <div dir='ltr' className="flex items-center justify-center gap-4 mt-12 pt-8 border-t border-slate-100">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        <ChevronLeft size={16} />
        Pre
      </button>

      <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-white font-bold shadow-md shadow-primary/30">
        {currentPage}
      </div>

      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={!hasMore} // این بولین رو باید از بک‌اند بگیریم (مثلا اگه results کمتر از لیمیت بود یعنی صفحه بعدی نیست)
        className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        Next
        <ChevronRight size={16} />
      </button>
    </div>
  );
};

export default Pagination;