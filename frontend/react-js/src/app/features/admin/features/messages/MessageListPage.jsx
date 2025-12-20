// src/app/features/admin/features/messages/MessageListPage.jsx
import { useState } from 'react';
import { Search, Mail, Eye, RotateCcw, ArrowUp, ArrowDown, User } from 'lucide-react';
import { useAdminMessages } from '../../hooks/useAdminMessages';
import MessageReplyModal from './components/MessageReplyModal'; // مسیر را تنظیم کنید

const MessageListPage = () => {
  const {
    messages,
    totalCount,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    sortConfig,
    handleSort,
    isLoading,
    replyMutation,
  } = useAdminMessages();

  const [selectedMessage, setSelectedMessage] = useState(null);

  // هندلر باز کردن مودال
  const openModal = (msg) => setSelectedMessage(msg);
  const closeModal = () => setSelectedMessage(null);

  // هندلر ارسال فرم
  const handleReplySubmit = (id, data) => {
    replyMutation.mutate({ id, reply_text: data.reply_text }, {
        onSuccess: () => closeModal()
    });
  };

  // کامپوننت هدر جدول
  const SortableHeader = ({ label, sortKey }) => (
    <th 
      className="cursor-pointer hover:bg-slate-100 transition-colors group select-none"
      onClick={() => handleSort(sortKey)}
    >
      <div className="flex items-center gap-2 text-slate-500 font-bold text-xs uppercase tracking-wider">
        {label}
        <span className={`transition-opacity ${sortConfig.key === sortKey ? 'opacity-100 text-primary' : 'opacity-0 group-hover:opacity-40'}`}>
          {sortConfig.key === sortKey && sortConfig.direction === 'asc' ? <ArrowUp size={14}/> : <ArrowDown size={14}/>}
        </span>
      </div>
    </th>
  );

  return (
    <div className="space-y-6 pb-20">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-3xl border border-slate-100 shadow-sm">
        <div className="flex items-center gap-4">
            <div className="bg-blue-50 text-blue-600 p-4 rounded-2xl">
                <Mail size={28} />
            </div>
            <div>
                <h1 className="text-2xl font-black text-slate-800">صندوق پیام‌ها</h1>
                <p className="text-slate-500 text-sm mt-1">مدیریت پیام‌های "تماس با ما" و پشتیبانی</p>
            </div>
        </div>
        <div className="flex items-center gap-3">
             <div className="stats shadow-sm border border-slate-100 rounded-2xl bg-white">
                <div className="stat py-2 px-6 place-items-center">
                    <div className="stat-title text-xs">کل پیام‌ها</div>
                    <div className="stat-value text-primary text-2xl">{totalCount}</div>
                </div>
             </div>
        </div>
      </div>

      {/* Toolbar */}
      <div className="sticky top-2 z-10 bg-white/80 backdrop-blur-xl p-2 rounded-2xl border border-slate-200/60 shadow-lg shadow-slate-200/20 flex gap-4">
         <div className="relative flex-1">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
            <input 
              type="text" 
              placeholder="جستجو در نام، ایمیل، موضوع..." 
              className="input input-ghost w-full pr-10 focus:bg-white transition-all rounded-xl"
              value={searchQuery}
              onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
              }}
            />
         </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden min-h-[400px]">
        <div className="overflow-x-auto">
          <table className="table w-full">
            <thead className="bg-slate-50 border-b border-slate-100 h-14">
              <tr>
                <SortableHeader label="#" sortKey="id" />
                <SortableHeader label="کاربر" sortKey="full_name" />
                <SortableHeader label="موضوع پیام" sortKey="subject" />
                <SortableHeader label="تاریخ" sortKey="created_at" />
                <th className="text-center w-24">عملیات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {isLoading ? (
                 <tr>
                    <td colSpan="5" className="h-64 text-center">
                        <span className="loading loading-spinner loading-lg text-primary"></span>
                    </td>
                 </tr>
              ) : messages.length === 0 ? (
                 <tr>
                    <td colSpan="5" className="h-64 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
                        <Mail size={40} className="opacity-20"/>
                        پیامی یافت نشد
                    </td>
                 </tr>
              ) : (
                messages.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="font-mono text-xs text-slate-400 text-start">{item.id}</td>
                    
                    <td className='text-start'>
                      <div className="flex items-center gap-3">
                        <div className="avatar placeholder">
                          <div className="bg-primary text-white rounded-full w-10 h-10 ring-1 ring-slate-200 flex items-center justify-center">
                             <span className="text-xs font-bold">{item.full_name?.[0] || <User size={16}/>}</span>
                          </div>
                        </div>
                        <div className="flex flex-col">
                          <span className="font-bold text-slate-700 text-sm">{item.full_name}</span>
                          <span className="text-[11px] text-slate-400 font-mono dir-ltr text-right">{item.email}</span>
                        </div>
                      </div>
                    </td>

                    <td className="max-w-xs text-start">
                        <div className="font-medium text-slate-800 text-sm truncate" title={item.subject}>
                            {item.subject}
                        </div>
                        <div className="text-xs text-slate-500 truncate max-w-[200px] opacity-70">
                            {item.message}
                        </div>
                    </td>

                    <td className='text-start'>
                        <div className="badge badge-ghost badge-sm font-mono text-xs opacity-70">
                            {new Date(item.created_at).toLocaleDateString('fa-IR')}
                        </div>
                    </td>

                    <td className='text-start'>
                        <button 
                            onClick={() => openModal(item)}
                            className="btn btn-sm btn-ghost text-primary bg-primary/5 hover:bg-primary hover:text-white gap-2 transition-all w-full"
                        >
                            <Eye size={16} />
                            <span className="hidden sm:inline">بررسی</span>
                        </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex justify-center dir-ltr">
                <div className="join bg-white shadow-sm border border-slate-200 rounded-lg">
                    {[...Array(totalPages)].map((_, i) => (
                        <button
                            key={i}
                            className={`join-item btn btn-sm ${currentPage === i + 1 ? 'btn-primary text-white' : 'btn-ghost'}`}
                            onClick={() => setCurrentPage(i + 1)}
                        >
                            {i + 1}
                        </button>
                    ))}
                </div>
            </div>
        )}
      </div>

      {/* Modal */}
      <MessageReplyModal 
        isOpen={!!selectedMessage}
        message={selectedMessage}
        onClose={closeModal}
        onSubmit={handleReplySubmit}
        isPending={replyMutation.isPending}
      />

    </div>
  );
};

export default MessageListPage;