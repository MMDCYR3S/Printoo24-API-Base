import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { UploadCloud, File, X, CheckCircle, ArrowLeft, Image as ImageIcon, Eye, Trash2 } from 'lucide-react';
import { cartService } from '../../../services/cartService';
import { toast } from 'react-hot-toast';

const DesignUploadPage = () => {
  const { itemId } = useParams();
  const navigate = useNavigate();
  
  const [serverFiles, setServerFiles] = useState([]);
  const [pendingFiles, setPendingFiles] = useState([]);
  const [loadingItem, setLoadingItem] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchItemDetails();
  }, [itemId]);

  const fetchItemDetails = async () => {
    try {
      setLoadingItem(true);
      const data = await cartService.getItem(itemId);
      if (data && data.uploads) {
        setServerFiles(data.uploads);
      }
    } catch (err) {
      console.error(err);
      toast.error('هەڵە لە وەرگرتنی زانیاری فایلەکان');
    } finally {
      setLoadingItem(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files).map(file => ({
        file,
        id: Math.random().toString(36).substr(2, 9),
        preview: URL.createObjectURL(file),
        status: 'pending' 
      }));
      setPendingFiles(prev => [...prev, ...newFiles]);
    }
    e.target.value = ''; 
  };

  const removePendingFile = (tempId) => {
    setPendingFiles(prev => prev.filter(f => f.id !== tempId));
  };

  const handleUploadPending = async () => {
    if (pendingFiles.length === 0) return;

    setIsUploading(true);
    let successCount = 0;
    const queue = [...pendingFiles];

    for (const item of queue) {
      if (item.status === 'success') continue;

      try {
        setPendingFiles(prev => prev.map(f => f.id === item.id ? { ...f, status: 'uploading' } : f));
        await cartService.uploadDesign(itemId, item.file);
        setPendingFiles(prev => prev.filter(f => f.id !== item.id));
        successCount++;
      } catch (err) {
        console.error(err);
        setPendingFiles(prev => prev.map(f => f.id === item.id ? { ...f, status: 'error' } : f));
        toast.error(` هەڵە لە بارکردنی ${item.file.name}`);
      }
    }

    if (successCount > 0) {
      toast.success(`${successCount} فایل بە سەرکەوتوویی پاشەکەوت کرا `);
      fetchItemDetails();
    }
    
    setIsUploading(false);
  };

  const handleDeleteServerFile = async (uploadId) => {
    if (!window.confirm('دڵنیایت لە سڕینەوەی فایلی دیزاین؟')) return;
    
    try {
      setDeletingId(uploadId);
      await cartService.deleteUpload(uploadId);
      setServerFiles(prev => prev.filter(f => f.id !== uploadId));
      toast.success('فایل بە سەرکەوتوویی سڕایەوە');
    } catch (err) {
      console.error( err);
      toast.error(' کێشەیەک لە سڕینەوەی فایل ڕوویدا');
    } finally {
      setDeletingId(null);
    }
  };

  const openImage = (url) => {
    window.open(url, '_blank');
  };

  if (loadingItem) {
    return <div className="min-h-screen flex items-center justify-center"><span className="loading loading-dots loading-lg text-primary"></span></div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 pb-24">
      <div className="max-w-4xl mx-auto space-y-6">
        
        <div className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-slate-100">
            <div>
                <h1 className="text-xl font-bold text-slate-800">بەڕێوەبردنی فایلەکانی داواکاری</h1>
                <p className="text-xs text-slate-500 mt-1"> {itemId}</p>
            </div>
            <button onClick={() => fetchItemDetails()} className="btn btn-ghost btn-sm text-xs">
 
            </button>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <h2 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                <UploadCloud className="text-blue-600"/>
                زیادکردنی فایلێکی نوێ
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
                    <h3 className="font-bold text-slate-700"> فایلەکان لێرە دابنێ</h3>
                    <p className="text-xs text-slate-400 mt-2">پشتگیری لە فۆرماتەکانی JPG, PNG, PDF, ZIP </p>
                </div>
            </div>
        </div>

        {pendingFiles.length > 0 && (
            <div className="bg-amber-50 p-6 rounded-3xl border border-amber-100 animate-in fade-in slide-in-from-bottom-4">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-amber-800 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                        فایلە ئامادەکانی ناردن ({pendingFiles.length})
                    </h3>
                    {isUploading && <span className="loading loading-spinner loading-sm text-amber-600"></span>}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
                    {pendingFiles.map((item) => (
                        <div key={item.id} className="bg-white p-3 rounded-xl border border-amber-200 flex items-center justify-between">
                            <div className="flex items-center gap-3 overflow-hidden">
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
                                {item.status === 'error' && <span className="text-xs text-red-500 font-bold">هەڵە</span>}
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
                    {isUploading ? ' لە بارکردندایە...' : 'دەستپێکردنی بارکردنی فایلەکان'}
                </button>
            </div>
        )}

        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm min-h-[200px]">
             <h2 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                <CheckCircle className="text-emerald-500"/>
               ({serverFiles.length})
            </h2>

            {serverFiles.length === 0 ? (
                <div className="text-center py-10 text-slate-400 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                    <ImageIcon size={48} className="mx-auto mb-2 opacity-50"/>
                    <p>هێشتا هیچ فایلێک بۆ ئەم داواکارییە تۆمار نەکراوە</p>
                </div>
            ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    {serverFiles.map((file, idx) => (
                        <div key={idx} className="group relative aspect-square bg-slate-100 rounded-2xl overflow-hidden border border-slate-200">
                            
                            {file.file_url.match(/\.(jpeg|jpg|png|gif|webp)$/i) ? (
                                <img src={file.file_url} alt="upload" className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 p-4 text-center">
                                    <File size={32} className="mb-2"/>
                                    <span className="text-xs break-all line-clamp-2" dir="ltr">{file.file_url.split('/').pop()}</span>
                                </div>
                            )}

                            {/* 🔴 این همون دکمه سطل زباله جیغ و ثابته! روی عکس میخکوب شده */}
                            <button 
                                onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDeleteServerFile(file.id); }}
                                disabled={deletingId === file.id}
                                className="absolute top-2 left-2 z-50 flex items-center justify-center w-8 h-8 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-all shadow-lg"
                                title="سڕینەوەی ئەم فایلە"
                            >
                                {deletingId === file.id ? (
                                    <span className="loading loading-spinner loading-xs"></span>
                                ) : (
                                    <Trash2 size={16} />
                                )}
                            </button>
                            
                            <div className="absolute top-2 right-2 z-30 bg-emerald-500/90 text-white text-[10px] px-2 py-1 rounded-md shadow-sm pointer-events-none">
                            تۆمارکرا
                            </div>

                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-sm z-20 pointer-events-none group-hover:pointer-events-auto">
                                <button 
                                    onClick={() => openImage(file.file_url)}
                                    className="p-3 bg-white text-slate-800 rounded-xl hover:scale-110 transition-transform shadow-lg pointer-events-auto"
                                    title="بینینی وێنە بە قەبارەی گەورەتر"
                                >
                                    <Eye size={20} />
                                </button>
                            </div>

                        </div>
                    ))}
                </div>
            )}
        </div>

      </div>

      <div className="fixed bottom-0 left-0 w-full bg-white border-t border-slate-200 p-4 shadow-[0_-5px_20px_rgba(0,0,0,0.05)] z-50">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
            <div className="flex-1 text-sm text-slate-500 hidden sm:block">
                {serverFiles.length > 0 
                  ? `${serverFiles.length} فایل بۆ چاپ ئامادەیە ` 
                  : ' هێشتا هیچ فایلێکت بار نەکردووە '}
            </div>
            
            <button
                onClick={() => navigate('/cart')}
                disabled={isUploading || pendingFiles.length > 0 || deletingId !== null} 
                className="btn btn-primary px-8 rounded-xl flex-1 sm:flex-none shadow-lg shadow-primary/30"
            >
                {pendingFiles.length > 0 
                    ? '  تکایە سەرەتا فایلە نوێیەکان باربکە ' 
                    : '  پەسەندکردنی کۆتایی و گەڕانەوە بۆ سەبەتی کڕین '}
                <ArrowLeft size={18} />
            </button>
        </div>
      </div>
    </div>
  );
};

export default DesignUploadPage;