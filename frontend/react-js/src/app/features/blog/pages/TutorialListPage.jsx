import React from 'react';
import { Film, AlertCircle } from 'lucide-react';
import SEO from '../../../components/common/SEO';
import { useTutorials } from '../hooks/useTutorials';
import TutorialCard from '../components/TutorialCard';
import TutorialModal from '../components/TutorialModal';

// اسکلتون برای زمان لودینگ لیست
const TutorialSkeleton = () => (
  <div className="bg-white rounded-3xl overflow-hidden border border-slate-100 shadow-sm flex flex-col h-full animate-pulse">
    <div className="aspect-video bg-slate-200 w-full" />
    <div className="p-5 flex flex-col flex-1 gap-4">
      <div className="h-6 bg-slate-200 rounded-md w-3/4 mt-2" />
      <div className="mt-auto pt-4 border-t border-slate-100">
        <div className="h-4 bg-slate-200 rounded w-1/3" />
      </div>
    </div>
  </div>
);

const TutorialListPagePublic = () => {
  const {
    tutorials,
    isLoadingList,
    listError,
    selectedTutorial,
    isLoadingDetail,
    detailError,
    isModalOpen,
    handleOpenTutorial,
    handleCloseModal
  } = useTutorials();

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl" dir="rtl">
      <SEO 
        title="فێرکارییە ڤیدیۆییەکان" 
        description="ویدیوهای آموزشی پرینتو۲۴ را تماشا کنید و مهارت‌های چاپ و طراحی خود را ارتقا دهید."
        keywords="آموزش چاپ, ویدیو آموزشی, پرینتو۲۴, طراحی برای چاپ"
      />

      {/* ── هدر صفحه ── */}
      <div className="mb-12 text-center md:text-right border-b border-slate-100 pb-8 flex flex-col md:flex-row items-center gap-6">
        <div className="p-5 bg-primary/10 rounded-[28px] text-primary shrink-0">
          <Film size={48} />
        </div>
        <div>
          <h1 className="text-3xl md:text-4xl font-black text-slate-800 mb-3">
          فێرکارییە ڤیدیۆییەکان          </h1>
          <p className="text-slate-500 max-w-2xl text-sm md:text-base leading-relaxed">
          لەم بەشەدا دەتوانیت نوێترین ڤیدیۆ فێرکارییەکانمان ببینیت. لە ئامۆژگارییەکانی دیزاینەوە تا ڕێنمایی هەڵبژاردنی بەرهەم، هەموو شتێک لێرەیە.
          </p>
        </div>
      </div>

      {/* ── لیست ویدیوها ── */}
      {listError ? (
        <div className="bg-red-50 border border-red-100 text-red-600 p-8 rounded-3xl flex flex-col items-center justify-center text-center gap-4 my-10">
          <AlertCircle size={48} className="text-red-400" />
          <p className="font-bold text-lg">{listError}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 md:gap-8">
          {isLoadingList ? (
            Array.from({ length: 8 }).map((_, idx) => <TutorialSkeleton key={idx} />)
          ) : tutorials.length > 0 ? (
            tutorials.map((tutorial) => (
              <TutorialCard 
                key={tutorial.id} 
                tutorial={tutorial} 
                onClick={handleOpenTutorial} 
              />
            ))
          ) : (
            <div className="col-span-full py-24 flex flex-col items-center justify-center text-center bg-slate-50 rounded-3xl border border-slate-200 border-dashed">
              <Film size={64} className="text-slate-300 mb-6" />
              <h3 className="text-xl font-bold text-slate-700 mb-2">هیچ ڤیدیۆیەک نەدۆزرایەوە</h3>
              <p className="text-slate-500 text-sm max-w-sm">
              هێشتا هیچ ڤیدیۆیەکی فێرکاری لەم بەشەدا بڵاونەکراوەتەوە. بە زوویی بە ڤیدیۆی نوێ دەگەڕێینەوە.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── کامپوننت مودال پخش ویدیو ── */}
      <TutorialModal 
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        tutorial={selectedTutorial}
        isLoading={isLoadingDetail}
        error={detailError}
      />
    </div>
  );
};

export default TutorialListPagePublic;