import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { UploadCloud, File, X, CheckCircle, ArrowLeft, Image as ImageIcon, Eye, Trash2 } from 'lucide-react';
import { cartService } from '../../../services/cartService';
import { toast } from 'react-hot-toast';

import pageText from '../../../lang/pages.json';
import globalText from '../../../lang/global.json';

const DesignUploadPage = () => {
  const { itemId } = useParams();
  const navigate = useNavigate();
  
  const [serverFiles, setServerFiles] = useState([]);
  const [pendingFiles, setPendingFiles] = useState([]);
  const [loadingItem, setLoadingItem] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const t = pageText.cart.designUploadPage;

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
      toast.error(t.receivedFileInfoError);
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
        toast.error(t.uploadFailed + " " + item.file.name);
      }
    }

    if (successCount > 0) {
      toast.success(successCount + " " + t.uploadSuccess);
      fetchItemDetails();
    }
    
    setIsUploading(false);
  };

  const handleDeleteServerFile = async (uploadId) => {
    if (!window.confirm(t.approveDeletionFile)) return;
    
    try {
      setDeletingId(uploadId);
      await cartService.deleteUpload(uploadId);
      setServerFiles(prev => prev.filter(f => f.id !== uploadId));
      toast.success(t.deleteSuccess);
    } catch (err) {
      console.error(t.deleteFailed, err);
      toast.error(t.deleteFileError);
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
                <h1 className="text-xl font-bold text-slate-800">{t.pageTitle}</h1>
                <p className="text-xs text-slate-500 mt-1">{t.orderId} {itemId}</p>
            </div>
            <button onClick={() => fetchItemDetails()} className="btn btn-ghost btn-sm text-xs">
                {t.refreshList}
            </button>
        </div>

        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
            <h2 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                <UploadCloud className="text-blue-600"/>
                {t.addNewFile}
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
                    <h3 className="font-bold text-slate-700">{t.dropzoneTitle}</h3>
                    <p className="text-xs text-slate-400 mt-2">{t.dropzoneHint}</p>
                </div>
            </div>
        </div>

        {pendingFiles.length > 0 && (
            <div className="bg-amber-50 p-6 rounded-3xl border border-amber-100 animate-in fade-in slide-in-from-bottom-4">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold text-amber-800 flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                        {t.pendingFilesTitle.replace('{{count}}', pendingFiles.length)}
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
                                {item.status === 'error' && <span className="text-xs text-red-500 font-bold">{t.errorStatus}</span>}
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
                    {isUploading ? t.uploadingStatus : t.startUploadBtn}
                </button>
            </div>
        )}

        <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm min-h-[200px]">
             <h2 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                <CheckCircle className="text-emerald-500"/>
                {t.registeredFilesTitle.replace('{{count}}', serverFiles.length)}
            </h2>

            {serverFiles.length === 0 ? (
                <div className="text-center py-10 text-slate-400 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                    <ImageIcon size={48} className="mx-auto mb-2 opacity-50"/>
                    <p>{t.noFilesRegistered}</p>
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
                            
                            <div className="absolute top-2 right-2 z-30 bg-emerald-500 text-white text-[10px] px-2 py-0.5 rounded-full shadow-sm">
                                {t.registeredStatus}
                            </div>

                            <div className={`absolute inset-0 transition-all flex items-center justify-center gap-3 backdrop-blur-sm z-20
                                ${deletingId === file.id ? 'bg-black/60 opacity-100' : 'bg-black/50 opacity-0 group-hover:opacity-100'}`}
                            >
                                <button 
                                    onClick={() => openImage(file.file_url)}
                                    className="p-3 bg-white text-slate-800 rounded-xl hover:scale-110 transition-transform shadow-lg"
                                    title={t.viewLarger}
                                >
                                    <Eye size={20} />
                                </button>
                                
                                <button 
                                    onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDeleteServerFile(file.id); }}
                                    disabled={deletingId === file.id}
                                    className="p-3 bg-red-500 text-white rounded-xl hover:bg-red-600 hover:scale-110 transition-transform shadow-lg disabled:opacity-50"
                                    title={t.deleteFile}
                                >
                                    {deletingId === file.id ? (
                                        <span className="loading loading-spinner loading-sm"></span>
                                    ) : (
                                        <Trash2 size={20} />
                                    )}
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
                  ? t.readyForPrint.replace('{{count}}', serverFiles.length) 
                  : t.noFilesUploadedYet}
            </div>
            
            <button
                onClick={() => navigate('/cart')}
                disabled={isUploading || pendingFiles.length > 0 || deletingId !== null} 
                className="btn btn-primary px-8 rounded-xl flex-1 sm:flex-none shadow-lg shadow-primary/30"
            >
                {pendingFiles.length > 0 
                    ? t.uploadPendingWarning 
                    : t.finalConfirmAndBack}
                <ArrowLeft size={18} />
            </button>
        </div>
      </div>
    </div>
  );
};

export default DesignUploadPage;