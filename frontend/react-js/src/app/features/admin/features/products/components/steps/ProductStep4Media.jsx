import React, { useState, useCallback, useEffect,  useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Image as ImageIcon, UploadCloud, Star,
  Film, FileText, Trash2, PlayCircle, CheckCircle2,
  Loader2, Plus, ChevronLeft, ChevronRight
} from 'lucide-react';
import clsx from 'clsx';
import toast from 'react-hot-toast';
import { adminProductService } from '../../../../services/adminProductService';

// ─── Helpers ────────────────────────────────────────────────────────────────
const getImageUrl = (img) => {
  if (img.preview) return img.preview;
  if (img.image?.startsWith('http')) return img.image;
  const BASE_API_URL = 'http://localhost:9010';
  return `${BASE_API_URL}${img.image}`;
};

// ─── Section Title ────────────────────────────────────────────────────────────
const SectionTitle = ({ step, icon: Icon, title, desc }) => (
  <div className="flex items-start gap-5 mb-8 pb-6 border-b border-slate-200/60">
    <div className="relative flex-shrink-0 mt-1">
      <div className="w-14 h-14 rounded-[1.25rem] bg-gradient-to-br from-blue-500/10 to-blue-500/5 flex items-center justify-center text-blue-600 shadow-sm border border-blue-500/10">
        <Icon size={26} strokeWidth={1.5} />
      </div>
      {step && (
        <div className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-blue-600 text-white text-sm font-black flex items-center justify-center shadow-lg shadow-blue-500/40 border-2 border-white">
          {step}
        </div>
      )}
    </div>
    <div className="pt-1.5">
      <h3 className="font-extrabold text-slate-800 text-2xl tracking-tight">{title}</h3>
      {desc && <p className="text-sm text-slate-500 mt-2 font-medium">{desc}</p>}
    </div>
  </div>
);


const moveImage = (index, direction) => {
  const newIndex = index + direction;
  if (newIndex < 0 || newIndex >= images.length) return;

  setImages((prev) => {
    const arr = [...prev];
    [arr[index], arr[newIndex]] = [arr[newIndex], arr[index]];
    // بعد از آپدیت state، با سرور sync می‌کنیم
    syncOrderWithServer(arr);
    return arr;
  });
};

// ─── Main Component ───────────────────────────────────────────────────────────
const ProductStep4Media = ({
  initialData,
  productId,
  onUploadImage,
  onUploadAttachment,
  onFinish,
}) => {
  const [images, setImages] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [uploadingState, setUploadingState] = useState({ type: null, progress: 0 });
  // تصویری که در حال حذف است (uniqueId)
  const [deletingImageId, setDeletingImageId] = useState(null);
  // پیوستی که در حال حذف است (uniqueId)
  const [deletingAttachmentId, setDeletingAttachmentId] = useState(null);
// ─── reorder ref ──────────────────────────────────────────────────────────
const reorderTimerRef = useRef(null);
  // ─── Init از سرور ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (initialData?.images && images.length === 0) {
      setImages(
        initialData.images.map((img) => ({
          ...img,
          uniqueId: img.id ? `server-img-${img.id}` : `server-img-${Math.random()}`,
        }))
      );
    }
    if (initialData?.attachments && attachments.length === 0) {
      setAttachments(
        initialData.attachments.map((att) => ({
          ...att,
          uniqueId: att.id ? `server-att-${att.id}` : `server-att-${Math.random()}`,
        }))
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialData]);

  // ─── 1. آپلود تصویر ───────────────────────────────────────────────────────
  const onDropImages = useCallback(
    async (acceptedFiles) => {
      if (!acceptedFiles?.length) return;
      if (!onUploadImage) return toast.error('خطا: توابع آپلود در دسترس نیست');

      setUploadingState({ type: 'image', progress: 10 });
      const toastId = toast.loading('در حال پردازش...');

      const newOptimisticImages = acceptedFiles.map((file) => ({
        file,
        preview: URL.createObjectURL(file),
        uniqueId: `temp-${Math.random()}`,
        isUploading: true,
        id: null,
      }));

      setImages((prev) => [...prev, ...newOptimisticImages]);

      try {
        for (let i = 0; i < newOptimisticImages.length; i++) {
          const optImg = newOptimisticImages[i];
          const formData = new FormData();
          formData.append('image', optImg.file);
          formData.append('order', images.length + i + 1);

          const result = await onUploadImage(formData);

          setImages((prev) =>
            prev.map((img) =>
              img.uniqueId === optImg.uniqueId
                ? {
                    ...img,
                    id: result.id,
                    image: result.image || optImg.preview,
                    isUploading: false,
                  }
                : img
            )
          );
        }
        toast.success('تصاویر با موفقیت آپلود شد', { id: toastId });
      } catch (error) {
        console.error(error);
        toast.error('خطا در آپلود تصاویر', { id: toastId });
        setImages((prev) => prev.filter((img) => !img.isUploading));
      } finally {
        setUploadingState({ type: null, progress: 0 });
      }
    },
    [onUploadImage, images.length]
  );

  // ─── 2. حذف تصویر (سرور + state) ─────────────────────────────────────────
  const removeImage = async (img) => {
    // اگر تصویر هنوز در حال آپلود است، فقط از state حذف می‌کنیم
    if (img.isUploading || !img.id) {
      setImages((prev) => prev.filter((i) => i.uniqueId !== img.uniqueId));
      return;
    }

    setDeletingImageId(img.uniqueId);
    const toastId = toast.loading('در حال حذف تصویر...');
    try {
      await adminProductService.deleteImage(productId, img.id);
      setImages((prev) => prev.filter((i) => i.uniqueId !== img.uniqueId));
      toast.success('تصویر حذف شد', { id: toastId });
    } catch (error) {
      console.error(error);
      toast.error('حذف تصویر ناموفق بود', { id: toastId });
    } finally {
      setDeletingImageId(null);
    }
  };

// ─── 3. جابجایی تصویر + sync با سرور ─────────────────────────────────────
const syncOrderWithServer = useCallback((newImages) => {
  const ids = newImages.filter((img) => img.id).map((img) => img.id);
  if (!ids.length) return;
  if (reorderTimerRef.current) clearTimeout(reorderTimerRef.current);
  reorderTimerRef.current = setTimeout(async () => {
    try {
      await adminProductService.reorderImages(productId, ids);
    } catch (error) {
      console.error('خطا در ذخیره ترتیب تصاویر:', error);
      toast.error('ترتیب تصاویر ذخیره نشد');
    }
  }, 600);
}, [productId]);

const moveImage = (index, direction) => {
  const newIndex = index + direction;
  if (newIndex < 0 || newIndex >= images.length) return;
  setImages((prev) => {
    const arr = [...prev];
    [arr[index], arr[newIndex]] = [arr[newIndex], arr[index]];
    syncOrderWithServer(arr);
    return arr;
  });
};
  // ─── 4. آپلود پیوست ───────────────────────────────────────────────────────
  const handleAttachmentUpload = async (e, type) => {
    const files = e.target.files;
    if (!files?.length) return;
    if (!onUploadAttachment) return toast.error('خطا: توابع آپلود در دسترس نیست');

    setUploadingState({ type, progress: 20 });
    const toastId = toast.loading('در حال آپلود فایل...');

    try {
      const formData = new FormData();
      formData.append('file', files[0]);
      formData.append('name', files[0].name);
      formData.append('product_id', productId);

      const result = await onUploadAttachment(formData);

      const newAtt = {
        id: result.id,
        file: result.file || URL.createObjectURL(files[0]),
        type,
        name: files[0].name,
        uniqueId: `temp-att-${Math.random()}`,
      };

      setAttachments((prev) => [...prev, newAtt]);
      toast.success('فایل با موفقیت ضمیمه شد', { id: toastId });
    } catch (error) {
      toast.error('آپلود ناموفق بود', { id: toastId });
    } finally {
      setUploadingState({ type: null, progress: 0 });
      e.target.value = '';
    }
  };

  // ─── 5. حذف پیوست (سرور + state) ─────────────────────────────────────────
  const removeAttachment = async (att) => {
    // اگر id ندارد (هنوز آپلود نشده) فقط از state پاک می‌کنیم
    if (!att.id) {
      setAttachments((prev) => prev.filter((a) => a.uniqueId !== att.uniqueId));
      return;
    }

    setDeletingAttachmentId(att.uniqueId);
    const toastId = toast.loading('در حال حذف فایل...');
    try {
      await adminProductService.deleteAttachment(productId, att.id);
      setAttachments((prev) => prev.filter((a) => a.uniqueId !== att.uniqueId));
      toast.success('فایل حذف شد', { id: toastId });
    } catch (error) {
      console.error(error);
      toast.error('حذف فایل ناموفق بود', { id: toastId });
    } finally {
      setDeletingAttachmentId(null);
    }
  };

  // ─── 6. اتمام ─────────────────────────────────────────────────────────────
  const handleFinalFinish = () => {
    const isAnyUploading =
      images.some((img) => img.isUploading) || uploadingState.type !== null;
    if (isAnyUploading) return toast.error('لطفاً صبر کنید تا آپلود تمام شود');

    toast.success('محصول با موفقیت ذخیره و تکمیل شد!');
    if (onFinish) onFinish();
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: onDropImages,
    accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
    multiple: true,
  });

  // ─── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-6xl mx-auto pb-40 space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-500">

      {/* ═══ SECTION 1: IMAGES ═══ */}
      <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 md:p-10 rounded-[2rem] transition-all hover:shadow-blue-500/5">
        <SectionTitle
          step="4"
          icon={ImageIcon}
          title="گالری تصاویر"
          desc="تصاویر محصول را آپلود کنید (عکس اول به عنوان کاور استفاده می‌شود — با فلش‌ها ترتیب را تغییر دهید)"
        />

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={clsx(
            'border-2 border-dashed rounded-[2rem] p-10 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group mb-10',
            isDragActive
              ? 'border-blue-500 bg-blue-500/5 shadow-inner'
              : 'border-slate-200 hover:border-blue-500/40 hover:bg-slate-50'
          )}
        >
          <input {...getInputProps()} />
          <div className="w-20 h-20 rounded-full bg-white shadow-sm flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            {uploadingState.type === 'image' ? (
              <Loader2 size={36} className="text-blue-600 animate-spin" />
            ) : (
              <UploadCloud
                size={36}
                className={clsx(
                  'transition-colors',
                  isDragActive ? 'text-blue-600' : 'text-slate-400 group-hover:text-blue-600'
                )}
              />
            )}
          </div>
          <p className="text-lg font-extrabold text-slate-700">تصاویر را اینجا رها کنید</p>
          <p className="text-xs text-slate-400 mt-2 font-medium">
            یا برای انتخاب فایل کلیک کنید (فرمت‌های JPG, PNG, WEBP)
          </p>
        </div>

        {/* Image Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-5">
          <AnimatePresence>
            {images.map((img, index) => {
              const isDeleting = deletingImageId === img.uniqueId;
              const isFirst = index === 0;
              const isLast = index === images.length - 1;

              return (
                <motion.div
                  layout
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.5 }}
                  key={img.uniqueId}
                  className="relative aspect-square group rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all border border-slate-100"
                >
                  {/* تصویر */}
                  <div className={clsx('w-full h-full bg-slate-100 transition-all', (img.isUploading || isDeleting) && 'opacity-50')}>
                    <img
                      src={getImageUrl(img)}
                      alt=""
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                      onError={(e) => { e.target.src = '/placeholder.png'; }}
                    />
                  </div>

                  {/* لودینگ (آپلود یا حذف) */}
                  {(img.isUploading || isDeleting) && (
                    <div className="absolute inset-0 bg-white/50 backdrop-blur-sm flex items-center justify-center z-20">
                      <div className="p-3 bg-white rounded-xl shadow-lg">
                        <Loader2 size={24} className="animate-spin text-blue-600" />
                      </div>
                    </div>
                  )}

                  {/* hover overlay */}
                  {!img.isUploading && !isDeleting && (
                    <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px] opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-3 z-10">
                      {/* دکمه حذف */}
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); removeImage(img); }}
                        className="w-10 h-10 flex items-center justify-center bg-error/90 text-white rounded-full hover:bg-error hover:scale-110 transition-all shadow-lg"
                        title="حذف تصویر"
                      >
                        <Trash2 size={18} />
                      </button>

                      {/* دکمه‌های جابجایی */}
                      <div className="flex items-center gap-2">
                        {/* فلش راست = index کمتر = به سمت کاور */}
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); moveImage(index, -1); }}
                          disabled={isFirst}
                          className={clsx(
                            'w-8 h-8 flex items-center justify-center rounded-full transition-all shadow-md',
                            isFirst
                              ? 'bg-white/30 text-white/30 cursor-not-allowed'
                              : 'bg-white/90 text-slate-700 hover:bg-white hover:scale-110'
                          )}
                          title="انتقال به راست"
                        >
                          <ChevronRight size={16} />
                        </button>

                        {/* فلش چپ = index بیشتر */}
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); moveImage(index, +1); }}
                          disabled={isLast}
                          className={clsx(
                            'w-8 h-8 flex items-center justify-center rounded-full transition-all shadow-md',
                            isLast
                              ? 'bg-white/30 text-white/30 cursor-not-allowed'
                              : 'bg-white/90 text-slate-700 hover:bg-white hover:scale-110'
                          )}
                          title="انتقال به چپ"
                        >
                          <ChevronLeft size={16} />
                        </button>
                      </div>
                    </div>
                  )}

                  {/* badge کاور / شماره */}
                  <div className="absolute top-3 right-3 pointer-events-none z-10">
                    {isFirst ? (
                      <span className="flex items-center gap-1 bg-gradient-to-r from-amber-400 to-orange-500 text-white px-2.5 py-1 rounded-lg text-[10px] font-black shadow-lg shadow-orange-500/30 border border-white/20">
                        <Star size={12} fill="currentColor" /> کاور اصلی
                      </span>
                    ) : (
                      <span className="bg-white/90 backdrop-blur-md text-slate-700 px-2 py-0.5 rounded-md text-[10px] font-black shadow-sm">
                        #{index + 1}
                      </span>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>

        {images.length === 0 && (
          <div className="text-center py-6 text-slate-400 font-medium text-sm">
            هنوز تصویری اضافه نشده است.
          </div>
        )}
      </div>

      {/* ═══ SECTION 2: ATTACHMENTS ═══ */}
      <div className="bg-white/70 backdrop-blur-xl shadow-2xl shadow-slate-200/50 border border-white p-8 md:p-10 rounded-[2rem] transition-all hover:shadow-blue-500/5">
        <SectionTitle
          step="5"
          icon={FileText}
          title="فایل‌های ضمیمه"
          desc="ویدیوها، قالب‌های راهنما و فایل‌های مرتبط با محصول"
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">

          {/* ─ ویدیوها ─ */}
          <div className="bg-slate-50/50 rounded-3xl p-6 border border-slate-100">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-rose-100 text-rose-500 rounded-xl"><Film size={20} /></div>
                <h3 className="font-extrabold text-lg text-slate-800">ویدیوها</h3>
              </div>
              <div>
                <input type="file" id="video-upload" className="hidden" accept="video/*" onChange={(e) => handleAttachmentUpload(e, 'video')} />
                <label htmlFor="video-upload" className="flex items-center gap-2 bg-white border border-rose-200 text-rose-600 hover:bg-rose-50 px-4 py-2 rounded-full text-sm font-bold cursor-pointer transition-colors shadow-sm">
                  {uploadingState.type === 'video' ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                  افزودن ویدیو
                </label>
              </div>
            </div>

            <div className="space-y-3">
              {attachments
                .filter((a) => a.type === 'video' || a.name?.endsWith('.mp4'))
                .map((vid) => {
                  const isDeleting = deletingAttachmentId === vid.uniqueId;
                  return (
                    <div key={vid.uniqueId} className="flex items-center gap-4 p-4 bg-white border border-slate-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow group">
                      <div className="w-10 h-10 bg-slate-50 rounded-full flex items-center justify-center text-slate-400 group-hover:text-rose-500 group-hover:bg-rose-50 transition-colors shrink-0">
                        <PlayCircle size={20} />
                      </div>
                      <span className="flex-1 text-sm font-bold text-slate-700 truncate" dir="ltr">
                        {vid.name || 'video_file.mp4'}
                      </span>
                      <button
                        onClick={() => removeAttachment(vid)}
                        disabled={isDeleting}
                        className="w-8 h-8 flex items-center justify-center text-slate-300 hover:text-error hover:bg-red-50 rounded-full transition-colors shrink-0"
                      >
                        {isDeleting
                          ? <Loader2 size={16} className="animate-spin text-slate-400" />
                          : <Trash2 size={16} />
                        }
                      </button>
                    </div>
                  );
                })}

              {attachments.filter((a) => a.type === 'video' || a.name?.endsWith('.mp4')).length === 0 && (
                <div className="text-center py-6 text-slate-400 text-xs font-medium border-2 border-dashed border-slate-200 rounded-2xl">
                  ویدیویی آپلود نشده است
                </div>
              )}
            </div>
          </div>

          {/* ─ قالب‌ها و اسناد ─ */}
          <div className="bg-slate-50/50 rounded-3xl p-6 border border-slate-100">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-100 text-emerald-600 rounded-xl"><FileText size={20} /></div>
                <h3 className="font-extrabold text-lg text-slate-800">قالب‌ها و اسناد</h3>
              </div>
              <div>
                <input type="file" id="doc-upload" className="hidden" accept=".pdf,.zip,.rar,.ai,.psd" onChange={(e) => handleAttachmentUpload(e, 'doc')} />
                <label htmlFor="doc-upload" className="flex items-center gap-2 bg-white border border-emerald-200 text-emerald-600 hover:bg-emerald-50 px-4 py-2 rounded-full text-sm font-bold cursor-pointer transition-colors shadow-sm">
                  {uploadingState.type === 'doc' ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                  ضمیمه فایل
                </label>
              </div>
            </div>

            <div className="space-y-3">
              {attachments
                .filter((a) => a.type === 'doc' || (!a.type && !a.name?.endsWith('.mp4')))
                .map((doc) => {
                  const isDeleting = deletingAttachmentId === doc.uniqueId;
                  return (
                    <div key={doc.uniqueId} className="flex items-center gap-4 p-4 bg-white border border-slate-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow group">
                      <div className="w-10 h-10 bg-slate-50 rounded-full flex items-center justify-center text-slate-400 group-hover:text-emerald-500 group-hover:bg-emerald-50 transition-colors shrink-0">
                        <FileText size={20} />
                      </div>
                      <span className="flex-1 text-sm font-bold text-slate-700 truncate" dir="ltr">
                        {doc.name || 'document_file.pdf'}
                      </span>
                      <button
                        onClick={() => removeAttachment(doc)}
                        disabled={isDeleting}
                        className="w-8 h-8 flex items-center justify-center text-slate-300 hover:text-error hover:bg-red-50 rounded-full transition-colors shrink-0"
                      >
                        {isDeleting
                          ? <Loader2 size={16} className="animate-spin text-slate-400" />
                          : <Trash2 size={16} />
                        }
                      </button>
                    </div>
                  );
                })}

              {attachments.filter((a) => a.type === 'doc' || (!a.type && !a.name?.endsWith('.mp4'))).length === 0 && (
                <div className="text-center py-6 text-slate-400 text-xs font-medium border-2 border-dashed border-slate-200 rounded-2xl">
                  فایلی ضمیمه نشده است
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ═══ Footer ═══ */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex justify-center w-full px-6 pointer-events-none">
        <div className="bg-white/80 backdrop-blur-md p-3 rounded-full shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] border border-white/50 pointer-events-auto">
          <button
            onClick={handleFinalFinish}
            disabled={uploadingState.type !== null}
            className="btn bg-blue-600 hover:bg-blue-700 text-white h-14 px-12 rounded-full shadow-lg shadow-blue-500/40 text-lg font-black hover:scale-[1.02] active:scale-95 transition-all gap-3 border-none flex items-center"
          >
            <CheckCircle2 size={24} />
            اتمام و بازگشت به لیست محصولات
          </button>
        </div>
      </div>

    </div>
  );
};

export default ProductStep4Media;