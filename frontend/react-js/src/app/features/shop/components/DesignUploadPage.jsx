import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  UploadCloud,
  File,
  X,
  CheckCircle,
  ArrowLeft,
  Image as ImageIcon,
  Eye,
  Trash2,
  RefreshCw,
  FileText,
  FileArchive,
  AlertCircle,
  CloudUpload,
  Loader2,
  ImageOff,
  FolderOpen,
} from 'lucide-react';
import { cartService } from '../../../services/cartService';
import { toast } from 'react-hot-toast';

import pageText from '../../../lang/pages.json';
import globalText from '../../../lang/global.json';

/* ─────────────────────────────────────────────
   انیمیشن‌ها
   ───────────────────────────────────────────── */
const staggerContainer = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.04, delayChildren: 0.05 },
  },
};

const fadeUp = {
  hidden: { opacity: 0, y: 14 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 260, damping: 24 },
  },
  exit: {
    opacity: 0,
    y: -10,
    scale: 0.95,
    transition: { duration: 0.2 },
  },
};

/* ─────────────────────────────────────────────
   آیکون فایل بر اساس نوع
   ───────────────────────────────────────────── */
const getFileIcon = (type, name) => {
  if (type?.startsWith('image/')) return ImageIcon;
  if (type?.includes('pdf') || name?.endsWith('.pdf')) return FileText;
  if (type?.includes('zip') || type?.includes('rar') || name?.match(/\.(zip|rar|7z)$/i)) return FileArchive;
  return File;
};

const getFileColor = (type, name) => {
  if (type?.startsWith('image/')) return { bg: 'bg-blue-50', text: 'text-blue-500', ring: 'ring-blue-100' };
  if (type?.includes('pdf') || name?.endsWith('.pdf')) return { bg: 'bg-red-50', text: 'text-red-500', ring: 'ring-red-100' };
  if (type?.includes('zip') || type?.includes('rar')) return { bg: 'bg-amber-50', text: 'text-amber-500', ring: 'ring-amber-100' };
  return { bg: 'bg-slate-50', text: 'text-slate-400', ring: 'ring-slate-100' };
};

/* ═════════════════════════════════════════════
   DesignUploadPage
   ═════════════════════════════════════════════ */
const DesignUploadPage = () => {
  const { itemId } = useParams();
  const navigate = useNavigate();

  const [serverFiles, setServerFiles] = useState([]);
  const [pendingFiles, setPendingFiles] = useState([]);
  const [loadingItem, setLoadingItem] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const t = pageText.cart.designUploadPage;

  useEffect(() => {
    fetchItemDetails();
  }, [itemId]);

  const fetchItemDetails = async () => {
    try {
      setLoadingItem(true);
      const data = await cartService.getItem(itemId);
      if (data?.uploads) setServerFiles(data.uploads);
    } catch (err) {
      console.error(err);
      toast.error(t.receivedFileInfoError);
    } finally {
      setLoadingItem(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchItemDetails();
    setTimeout(() => setRefreshing(false), 600);
  };

  const processNewFiles = useCallback((files) => {
    const newFiles = Array.from(files).map((file) => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null,
      status: 'pending',
    }));
    setPendingFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files?.length > 0) processNewFiles(e.target.files);
    e.target.value = '';
  };

  // Drag & Drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = () => setIsDragging(false);
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.length > 0) processNewFiles(e.dataTransfer.files);
  };

  const removePendingFile = (tempId) => {
    setPendingFiles((prev) => prev.filter((f) => f.id !== tempId));
  };

  const handleUploadPending = async () => {
    if (pendingFiles.length === 0) return;

    setIsUploading(true);
    let successCount = 0;
    const queue = [...pendingFiles];

    for (const item of queue) {
      if (item.status === 'success') continue;
      try {
        setPendingFiles((prev) =>
          prev.map((f) => (f.id === item.id ? { ...f, status: 'uploading' } : f))
        );
        await cartService.uploadDesign(itemId, item.file);
        setPendingFiles((prev) => prev.filter((f) => f.id !== item.id));
        successCount++;
      } catch (err) {
        console.error(err);
        setPendingFiles((prev) =>
          prev.map((f) => (f.id === item.id ? { ...f, status: 'error' } : f))
        );
        toast.error(t.uploadFailed + ' ' + item.file.name);
      }
    }

    if (successCount > 0) {
      toast.success(successCount + ' ' + t.uploadSuccess);
      fetchItemDetails();
    }
    setIsUploading(false);
  };

  const handleDeleteServerFile = async (uploadId) => {
    if (!window.confirm(t.approveDeletionFile)) return;
    try {
      setDeletingId(uploadId);
      await cartService.deleteUpload(uploadId);
      setServerFiles((prev) => prev.filter((f) => f.id !== uploadId));
      toast.success(t.deleteSuccess);
    } catch (err) {
      console.error(t.deleteFailed, err);
      toast.error(t.deleteFileError);
    } finally {
      setDeletingId(null);
    }
  };

  const openImage = (url) => window.open(url, '_blank');

  const totalUploaded = serverFiles.length;
  const hasPending = pendingFiles.length > 0;

  /* ── لودینگ اولیه ── */
  if (loadingItem) return <PageSkeleton />;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100/50 pb-28">
      <div className="max-w-4xl mx-auto px-4 py-6 space-y-5">

        {/* ════════════════ هدر ════════════════ */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="
            flex items-center justify-between
            bg-white rounded-2xl
            ring-1 ring-black/[0.04]
            shadow-sm
            px-5 py-4
          "
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <CloudUpload size={20} className="text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-extrabold text-slate-800">{t.pageTitle}</h1>
              <p className="text-[11px] text-slate-400 font-medium mt-0.5">
                {t.orderId} <span className="font-bold text-slate-500 dir-ltr">{itemId}</span>
              </p>
            </div>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="
              w-9 h-9 flex items-center justify-center rounded-xl
              text-slate-400 hover:text-primary
              hover:bg-primary/8
              active:scale-95
              transition-all duration-200
            "
          >
            <RefreshCw
              size={17}
              className={refreshing ? 'animate-spin' : ''}
            />
          </button>
        </motion.div>

        {/* ════════════════ Dropzone ════════════════ */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-white rounded-2xl ring-1 ring-black/[0.04] shadow-sm overflow-hidden"
        >
          <div className="px-5 py-4 border-b border-slate-100/80">
            <h2 className="text-sm font-bold text-slate-700 flex items-center gap-2">
              <UploadCloud size={18} className="text-blue-500" />
              {t.addNewFile}
            </h2>
          </div>

          <div className="p-5">
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className="relative"
            >
              <input
                type="file"
                multiple
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                disabled={isUploading}
                accept="image/*,application/pdf,.zip,.rar"
              />
              <div
                className={`
                  rounded-2xl p-8 md:p-10
                  flex flex-col items-center justify-center text-center
                  border-2 border-dashed
                  transition-all duration-300 ease-out
                  ${isDragging
                    ? 'border-primary bg-primary/5 scale-[1.01]'
                    : 'border-slate-200 bg-slate-50/50 hover:border-blue-300 hover:bg-blue-50/30'
                  }
                `}
              >
                <motion.div
                  animate={isDragging ? { y: -4, scale: 1.1 } : { y: 0, scale: 1 }}
                  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
                  className={`
                    w-16 h-16 rounded-2xl
                    flex items-center justify-center mb-4
                    transition-colors duration-300
                    ${isDragging
                      ? 'bg-primary/15 text-primary shadow-lg shadow-primary/10'
                      : 'bg-white text-blue-500 shadow-md shadow-black/5 ring-1 ring-black/[0.04]'
                    }
                  `}
                >
                  <UploadCloud size={28} strokeWidth={1.8} />
                </motion.div>
                <h3 className="font-bold text-slate-700 text-sm">
                  {isDragging ? 'فایل رو اینجا رها کنید' : t.dropzoneTitle}
                </h3>
                <p className="text-[11px] text-slate-400 mt-2 max-w-xs leading-relaxed">
                  {t.dropzoneHint}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* ════════════════ فایل‌های در انتظار ════════════════ */}
        <AnimatePresence>
          {hasPending && (
            <motion.div
              initial={{ opacity: 0, y: 16, height: 0 }}
              animate={{ opacity: 1, y: 0, height: 'auto' }}
              exit={{ opacity: 0, y: -10, height: 0 }}
              transition={{ type: 'spring', stiffness: 200, damping: 24 }}
              className="overflow-hidden"
            >
              <div className="
                bg-gradient-to-br from-amber-50 to-orange-50/50
                rounded-2xl ring-1 ring-amber-200/50
                overflow-hidden
              ">
                {/* هدر */}
                <div className="flex items-center justify-between px-5 py-3.5 border-b border-amber-100/60">
                  <h3 className="text-sm font-bold text-amber-800 flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                    {t.pendingFilesTitle.replace('{{count}}', pendingFiles.length)}
                  </h3>
                  {isUploading && (
                    <Loader2 size={16} className="text-amber-600 animate-spin" />
                  )}
                </div>

                {/* لیست */}
                <div className="p-4">
                  <motion.div
                    variants={staggerContainer}
                    initial="hidden"
                    animate="show"
                    className="space-y-2 mb-4"
                  >
                    <AnimatePresence mode="popLayout">
                      {pendingFiles.map((item) => {
                        const FileIcon = getFileIcon(item.file.type, item.file.name);
                        const colors = getFileColor(item.file.type, item.file.name);
                        const isError = item.status === 'error';
                        const isActive = item.status === 'uploading';

                        return (
                          <motion.div
                            key={item.id}
                            variants={fadeUp}
                            exit="exit"
                            layout
                            className={`
                              flex items-center gap-3
                              bg-white p-3 rounded-xl
                              ring-1 transition-all duration-200
                              ${isError
                                ? 'ring-red-200 bg-red-50/50'
                                : isActive
                                  ? 'ring-amber-200 bg-amber-50/30'
                                  : 'ring-amber-100/80 hover:ring-amber-200'
                              }
                            `}
                          >
                            {/* پیش‌نمایش / آیکون */}
                            {item.preview ? (
                              <img
                                src={item.preview}
                                alt=""
                                className="w-11 h-11 rounded-lg object-cover ring-1 ring-black/[0.05] shrink-0"
                              />
                            ) : (
                              <div className={`w-11 h-11 rounded-lg flex items-center justify-center shrink-0 ${colors.bg} ring-1 ${colors.ring}`}>
                                <FileIcon size={20} className={colors.text} />
                              </div>
                            )}

                            {/* اطلاعات */}
                            <div className="flex-1 min-w-0">
                              <p className="text-[13px] font-semibold text-slate-700 truncate">
                                {item.file.name}
                              </p>
                              <p className="text-[10px] text-slate-400 mt-0.5 font-medium">
                                {(item.file.size / 1024 / 1024).toFixed(2)} MB
                              </p>
                            </div>

                            {/* وضعیت / عملیات */}
                            <div className="flex items-center gap-1.5 shrink-0">
                              {isError && (
                                <span className="text-[10px] font-bold text-red-500 flex items-center gap-1">
                                  <AlertCircle size={12} />
                                  {t.errorStatus}
                                </span>
                              )}
                              {isActive ? (
                                <div className="w-8 h-8 flex items-center justify-center">
                                  <Loader2 size={16} className="text-amber-500 animate-spin" />
                                </div>
                              ) : (
                                <button
                                  onClick={() => removePendingFile(item.id)}
                                  className="
                                    w-8 h-8 flex items-center justify-center rounded-lg
                                    text-slate-400 hover:text-red-500
                                    hover:bg-red-50
                                    transition-colors duration-200
                                  "
                                >
                                  <X size={16} />
                                </button>
                              )}
                            </div>
                          </motion.div>
                        );
                      })}
                    </AnimatePresence>
                  </motion.div>

                  {/* دکمه آپلود */}
                  <button
                    onClick={handleUploadPending}
                    disabled={isUploading}
                    className="
                      w-full flex items-center justify-center gap-2
                      py-3 rounded-xl
                      bg-gradient-to-l from-amber-500 to-orange-500
                      text-white text-sm font-bold
                      shadow-lg shadow-amber-500/20
                      hover:shadow-xl hover:shadow-amber-500/30
                      hover:-translate-y-[1px]
                      active:translate-y-0
                      disabled:opacity-60 disabled:cursor-not-allowed
                      transition-all duration-200
                    "
                  >
                    {isUploading ? (
                      <>
                        <Loader2 size={16} className="animate-spin" />
                        {t.uploadingStatus}
                      </>
                    ) : (
                      <>
                        <UploadCloud size={16} />
                        {t.startUploadBtn}
                      </>
                    )}
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ════════════════ فایل‌های ثبت شده ════════════════ */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl ring-1 ring-black/[0.04] shadow-sm overflow-hidden"
        >
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100/80">
            <h2 className="text-sm font-bold text-slate-700 flex items-center gap-2">
              <CheckCircle size={18} className="text-emerald-500" />
              {t.registeredFilesTitle.replace('{{count}}', serverFiles.length)}
            </h2>
            {totalUploaded > 0 && (
              <span className="text-[11px] font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
                {totalUploaded} فایل
              </span>
            )}
          </div>

          <div className="p-5">
            {serverFiles.length === 0 ? (
              <div className="
                flex flex-col items-center justify-center
                py-12
                bg-slate-50/50 rounded-xl
                border border-dashed border-slate-200
              ">
                <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mb-3">
                  <FolderOpen size={24} strokeWidth={1.3} className="text-slate-300" />
                </div>
                <p className="text-sm font-medium text-slate-400">{t.noFilesRegistered}</p>
              </div>
            ) : (
              <motion.div
                variants={staggerContainer}
                initial="hidden"
                animate="show"
                className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3"
              >
                {serverFiles.map((file, idx) => {
                  const isImage = file.file_url.match(/\.(jpeg|jpg|png|gif|webp)$/i);
                  const isDeleting = deletingId === file.id;
                  const fileName = file.file_url.split('/').pop();

                  return (
                    <motion.div
                      key={file.id || idx}
                      variants={fadeUp}
                      className="
                        group relative aspect-square
                        rounded-xl overflow-hidden
                        ring-1 ring-black/[0.06]
                        bg-slate-100
                      "
                    >
                      {isImage ? (
                        <img
                          src={file.file_url}
                          alt="upload"
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                      ) : (
                        <div className="w-full h-full flex flex-col items-center justify-center gap-2 p-3 text-center bg-gradient-to-br from-slate-50 to-slate-100">
                          <File size={28} strokeWidth={1.3} className="text-slate-300" />
                          <span className="text-[10px] text-slate-400 font-medium break-all line-clamp-2 dir-ltr">
                            {fileName}
                          </span>
                        </div>
                      )}

                      {/* بج ثبت شده */}
                      <div className="
                        absolute top-2 right-2 z-10
                        px-2 py-0.5 rounded-md
                        bg-emerald-500/90 backdrop-blur-sm
                        text-white text-[9px] font-bold
                        shadow-sm
                      ">
                        {t.registeredStatus}
                      </div>

                      {/* اورلی عملیات */}
                      <div className={`
                        absolute inset-0 z-20
                        flex items-center justify-center gap-2.5
                        transition-all duration-300
                        ${isDeleting
                          ? 'bg-black/50 backdrop-blur-sm opacity-100'
                          : 'bg-gradient-to-t from-black/50 via-black/20 to-transparent opacity-0 group-hover:opacity-100'
                        }
                      `}>
                        <button
                          onClick={() => openImage(file.file_url)}
                          className="
                            w-10 h-10 flex items-center justify-center
                            bg-white/90 backdrop-blur-sm text-slate-700
                            rounded-xl shadow-lg
                            hover:scale-110 active:scale-95
                            transition-all duration-200
                          "
                          title={t.viewLarger}
                        >
                          <Eye size={18} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            handleDeleteServerFile(file.id);
                          }}
                          disabled={isDeleting}
                          className="
                            w-10 h-10 flex items-center justify-center
                            bg-red-500 text-white
                            rounded-xl shadow-lg
                            hover:bg-red-600 hover:scale-110 active:scale-95
                            disabled:opacity-50
                            transition-all duration-200
                          "
                          title={t.deleteFile}
                        >
                          {isDeleting ? (
                            <Loader2 size={16} className="animate-spin" />
                          ) : (
                            <Trash2 size={16} />
                          )}
                        </button>
                      </div>
                    </motion.div>
                  );
                })}
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>

      {/* ════════════════ Bottom Bar ════════════════ */}
      <div className="
        fixed bottom-0 left-0 w-full z-50
        bg-white/90 backdrop-blur-xl
        border-t border-slate-200/60
        shadow-[0_-4px_20px_-4px_rgba(0,0,0,0.06)]
      ">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center gap-4">
          {/* وضعیت */}
          <div className="flex-1 hidden sm:flex items-center gap-2 min-w-0">
            {totalUploaded > 0 ? (
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="text-[13px] text-slate-500 font-medium">
                  {t.readyForPrint.replace('{{count}}', totalUploaded)}
                </span>
              </div>
            ) : (
              <span className="text-md text-slate-400 font-medium">
                {t.noFilesUploadedYet}
              </span>
            )}
          </div>

          {/* دکمه تأیید */}
          <button
            onClick={() => navigate('/cart')}
            disabled={isUploading || hasPending || deletingId !== null}
            className="
              flex items-center justify-center gap-2
              px-8 py-4 rounded-xl
              bg-primary text-white text-md font-bold
              shadow-md shadow-primary/20
              hover:shadow-lg hover:shadow-primary/30
              hover:-translate-y-[1px]
              active:translate-y-0
              disabled:opacity-50 disabled:cursor-not-allowed disabled:translate-y-0 disabled:shadow-sm
              transition-all duration-200
              flex-1 sm:flex-none 
            "
          >
            {hasPending ? t.uploadPendingWarning : t.finalConfirmAndBack}
            <ArrowLeft size={25} />
          </button>
        </div>
      </div>
    </div>
  );
};

/* ═════════════════════════════════════════════
   اسکلتون لودینگ
   ═════════════════════════════════════════════ */
const shimmer =
  'relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/50 before:to-transparent';

const PageSkeleton = () => (
  <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100/50 pb-28">
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-5">
      {/* هدر */}
      <div className="bg-white rounded-2xl ring-1 ring-black/[0.04] px-5 py-4 flex items-center gap-3">
        <div className={`w-10 h-10 rounded-xl bg-slate-100 ${shimmer}`} />
        <div className="space-y-2 flex-1">
          <div className={`h-5 w-40 bg-slate-100 rounded-lg ${shimmer}`} />
          <div className={`h-3 w-24 bg-slate-50 rounded-lg ${shimmer}`} />
        </div>
      </div>
      {/* Dropzone */}
      <div className="bg-white rounded-2xl ring-1 ring-black/[0.04] p-5">
        <div className={`h-5 w-32 bg-slate-100 rounded-lg mb-4 ${shimmer}`} />
        <div className={`h-40 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200 ${shimmer}`} />
      </div>
      {/* گرید */}
      <div className="bg-white rounded-2xl ring-1 ring-black/[0.04] p-5">
        <div className={`h-5 w-36 bg-slate-100 rounded-lg mb-4 ${shimmer}`} />
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className={`aspect-square bg-slate-100/80 rounded-xl ${shimmer}`}
              style={{ animationDelay: `${i * 100}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  </div>
);

export default DesignUploadPage;