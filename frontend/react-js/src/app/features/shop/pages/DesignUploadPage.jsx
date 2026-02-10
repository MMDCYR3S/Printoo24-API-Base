import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { UploadCloud, File, X, CheckCircle, ArrowLeft, Image as ImageIcon, Eye, Trash2 } from 'lucide-react';
import { cartService } from '../../../services/cartService';
import { toast } from 'react-hot-toast';

const DesignUploadPage = () => {
  const { itemId } = useParams();
  const navigate = useNavigate();
  
  // فایل‌هایی که الان روی سرور هستند (قبلا آپلود شدن)
  const [serverFiles, setServerFiles] = useState([]);
  
  // فایل‌هایی که کاربر انتخاب کرده ولی هنوز دکمه آپلود رو نزده
  const [pendingFiles, setPendingFiles] = useState([]);
  
  const [loadingItem, setLoadingItem] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  // دریافت اطلاعات آیتم و فایل‌های قبلی هنگام لود صفحه
  useEffect(() => {
    fetchItemDetails();
  }, [itemId]);

  const fetchItemDetails = async () => {
    try {
      setLoadingItem(true);
      const data = await cartService.getItem(itemId);
      // طبق داکیومنت، آرایه uploads داخل دیتا هست
      if (data && data.uploads) {
        setServerFiles(data.uploads);
      }
    } catch (err) {
      console.error(err);
      toast.error('خطا در دریافت اطلاعات فایل‌ها');
    } finally {
      setLoadingItem(false);
    }
  };

  // هندل کردن انتخاب فایل (دراپ یا کلیک)
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map(file => ({
        file,
        id: Math.random().toString(36).substr(2, 9), // ID موقت برای UI
        preview: URL.createObjectURL(file), // پیش‌نمایش لوکال
        status: 'pending' // pending, uploading, success, error
      }));
      setPendingFiles(prev => [...prev, ...newFiles]);
    }
    e.target.value = ''; // ریست اینپوت
  };

  // حذف از صف انتظار (قبل از آپلود)
  const removePendingFile = (tempId) => {
    setPendingFiles(prev => prev.filter(f => f.id !== tempId));
  };

  // شروع عملیات آپلود برای فایل‌های جدید
  const handleUploadPending = async () => {
    if (pendingFiles.length === 0) return;

    setIsUploading(true);
    let successCount = 0;

    // کپی آرایه برای پیمایش
    const queue = [...pendingFiles];

    for (const item of queue) {
      // فقط اونایی که هنوز آپلود نشدن یا ارور دادن رو دوباره تلاش کن
      if (item.status === 'success') continue;

      try {
        // تغییر وضعیت به در حال آپلود در UI
        setPendingFiles(prev => prev.map(f => f.id === item.id ? { ...f, status: 'uploading' } : f));
        
        // فراخوانی API
        const res = await cartService.uploadDesign(itemId, item.file);
        
        // حذف از صف pending و اضافه کردن به لیست serverFiles
        setPendingFiles(prev => prev.filter(f => f.id !== item.id));
        
        // افزودن به لیست سرور (برای نمایش در گالری پایین)
        // فرض بر اینه که ریسپانس سرور ساختار فایل رو برمیگردونه. 
        // اگر برنگردوند، دوباره fetchItemDetails میکنیم.
        // اینجا فرض میکنیم باید دوباره فچ کنیم تا مطمئن بشیم دیتای سرور دقیقه
        successCount++;

      } catch (err) {
        console.error(err);
        setPendingFiles(prev => prev.map(f => f.id === item.id ? { ...f, status: 'error' } : f));
        toast.error(`خطا در آپلود ${item.file.name}`);
      }
    }

    if (successCount > 0) {
      toast.success(`${successCount} فایل با موفقیت ذخیره شد`);
      // به‌روزرسانی لیست سرور
      fetchItemDetails();
    }
    
    setIsUploading(false);
  };

  // باز کردن عکس در تب جدید
  const openImage = (url) => {
    window.open(url, '_blank');
  };

  if (loadingItem) {
    return <div className="min-h-screen flex items-center justify-center"><span className="loading loading-dots loading-lg"></span></div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 pb-24">
      <div className="max-w-4xl mx-auto space-y-6">
        
        {/* هدر صفحه */}
        <div className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
            <div>
                <h1 className="text-xl font-bold text-slate-800">مدیریت فایل‌های سفارش</h1>
                <p className="text-xs text-slate-500 mt-1">شناسه سفارش: {itemId}</p>
            </div>
            <button onClick={() => fetchItemDetails()} className="btn btn-ghost btn-sm text-xs">
                بروزرسانی لیست
            </button>
        </div>

        {/* ناحیه آپلود (دراپ زون) */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <h2 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                <UploadCloud className="text-blue-600"/>
                افزودن فایل جدید
            </h2>
            
            <div className="relative group">
                <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    disabled={isUploading}
                    accept="image/*,application/pdf,.zip,.rar"
                />
                <div className="border-2 border-dashed border-slate-300 group-hover:border-blue-500 bg-slate-50 group-hover:bg-blue-50/50 rounded-2xl p-10 flex flex-col items-center justify-center transition-all text-center h-48">
                    <div className="w-14 h-14 bg-white text-blue-600 rounded-full shadow-md flex items-center justify-center mb-3">
                        <UploadCloud size={28} />
                    </div>
                    <h3 className="font-bold text-slate-700">فایل‌ها را اینجا رها کنید</h3>
                    <p className="text-xs text-slate-400 mt-2">پشتیبانی از JPG, PNG, PDF, ZIP (تعداد نامحدود)</p>
                </div>
            </div>
        </div>

        {/* لیست در انتظار آپلود (Pending) */}
        {pendingFiles.length > 0 && (
            <div className="bg-amber-50 p-6 rounded-3xl border border-amber-100 animate-in fade-in slide-in-from-bottom-4">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-amber-800 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                        فایل‌های آماده ارسال ({pendingFiles.length})
                    </h3>
                    {isUploading && <span className="loading loading-spinner loading-sm text-amber-600"></span>}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                    {pendingFiles.map((item) => (
                        <div key={item.id} className="bg-white p-3 rounded-xl border border-amber-200 flex items-center justify-between">
                            <div className="flex items-center gap-3 overflow-hidden">
                                {/* پیش‌نمایش کوچک */}
                                {item.file.type.startsWith('image/') ? (
                                    <img src={item.preview} alt="" className="w-10 h-10 rounded-lg object-cover bg-slate-100" />
                                ) : (
                                    <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-slate-400"><File size={20}/></div>
                                )}
                                <div className="min-w-0">
                                    <p className="text-sm font-medium text-slate-700 truncate max-w-[150px]">{item.file.name}</p>
                                    <p className="text-[10px] text-slate-400">{(item.file.size / 1024 / 1024).toFixed(2)} MB</p>
                                </div>
                            </div>
                            
                            <div className="flex items-center gap-2">
                                {item.status === 'error' && <span className="text-xs text-red-500 font-bold">خطا</span>}
                                {item.status === 'uploading' ? (
                                    <span className="loading loading-spinner loading-xs"></span>
                                ) : (
                                    <button onClick={() => removePendingFile(item.id)} className="p-2 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded-lg transition-colors">
                                        <X size={18} />
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                <button 
                    onClick={handleUploadPending}
                    disabled={isUploading}
                    className="btn bg-amber-500 hover:bg-amber-600 text-white border-none w-full shadow-lg shadow-amber-500/20"
                >
                    {isUploading ? 'در حال آپلود...' : 'شروع آپلود فایل‌ها'}
                </button>
            </div>
        )}

        {/* گالری فایل‌های روی سرور (Uploaded) */}
        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm min-h-[200px]">
             <h2 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                <CheckCircle className="text-emerald-500"/>
                فایل‌های ثبت شده ({serverFiles.length})
            </h2>

            {serverFiles.length === 0 ? (
                <div className="text-center py-10 text-slate-400 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                    <ImageIcon size={48} className="mx-auto mb-2 opacity-50"/>
                    <p>هنوز فایلی برای این سفارش ثبت نشده است</p>
                </div>
            ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    {serverFiles.map((file, idx) => (
                        <div key={idx} className="group relative aspect-square bg-slate-100 rounded-2xl overflow-hidden border border-slate-200">
                            {/* نمایش تصویر یا آیکون فایل */}
                            {file.file_url.match(/\.(jpeg|jpg|png|gif|webp)$/i) ? (
                                <img src={file.file_url} alt="upload" className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 p-4 text-center">
                                    <File size={32} className="mb-2"/>
                                    <span className="text-xs break-all line-clamp-2">فایل ضمیمه</span>
                                </div>
                            )}

                            {/* کاور هاور برای مشاهده */}
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 backdrop-blur-sm">
                                <button 
                                    onClick={() => openImage(file.file_url)}
                                    className="p-2 bg-white text-slate-800 rounded-full hover:scale-110 transition-transform shadow-lg"
                                    title="مشاهده"
                                >
                                    <Eye size={20} />
                                </button>
                                {/* دکمه حذف (اگر API ساپورت کند، فعلا فقط ویو) */}
                            </div>
                            
                            {/* بج وضعیت */}
                            <div className="absolute top-2 right-2 bg-emerald-500 text-white text-[10px] px-2 py-0.5 rounded-full shadow-sm">
                                ثبت شده
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>

      </div>

      {/* فوتر ثابت پایین */}
      <div className="fixed bottom-0 left-0 w-full bg-white border-t border-slate-200 p-4 shadow-[0_-5px_20px_rgba(0,0,0,0.05)] z-50">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
            <div className="flex-1 text-sm text-slate-500 hidden sm:block">
                {serverFiles.length > 0 
                  ? `${serverFiles.length} فایل برای چاپ آماده است.` 
                  : 'هنوز فایلی آپلود نکرده‌اید.'}
            </div>
            
            <button
                onClick={() => navigate('/cart')}
                disabled={isUploading || pendingFiles.length > 0} // تا وقتی فایلی تو صف آپلوده، نذار بره
                className="btn btn-primary px-8 rounded-xl flex-1 sm:flex-none shadow-lg shadow-primary/30"
            >
                {pendingFiles.length > 0 
                    ? 'لطفا ابتدا فایل‌های جدید را آپلود کنید' 
                    : 'تایید نهایی و بازگشت به سبد خرید'}
                <ArrowLeft size={18} />
            </button>
        </div>
      </div>
    </div>
  );
};

export default DesignUploadPage;