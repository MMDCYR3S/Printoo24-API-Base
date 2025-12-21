// src/app/features/admin/features/messages/MessageListPage.jsx
import { useState } from 'react';
import { 
  Search, Mail, Eye, Trash2, ArrowUp, ArrowDown, 
  CheckCircle2, AlertCircle, Clock, MailOpen, Inbox 
} from 'lucide-react';
import { useAdminMessages } from '../../hooks/useAdminMessages';
import MessageReplyModal from './components/MessageReplyModal';

const MessageListPage = () => {
  const {
    messages,
    totalCount,
    totalPages,
    currentPage,
    setCurrentPage,
    searchQuery,
    setSearchQuery,
    statusFilter,
    setStatusFilter,
    sortConfig,
    handleSort,
    isLoading,
    replyMutation,
    deleteMutation
  } = useAdminMessages();

  const [selectedMessage, setSelectedMessage] = useState(null);

  // Handlers
  const handleDelete = (id) => {
    if (window.confirm('آیا از حذف این پیام اطمینان دارید؟ این عملیات غیرقابل بازگشت است.')) {
        deleteMutation.mutate(id);
    }
  };

  const handleReplySubmit = (id, data) => {
    replyMutation.mutate({ id, reply_text: data.reply_text }, {
        onSuccess: () => setSelectedMessage(null) // بستن مودال بعد از موفقیت
    });
  };

  const SortableHeader = ({ label, sortKey, className = "" }) => (
    <th 
      className={`cursor-pointer hover:bg-slate-100 transition-colors select-none group ${className}`}
      onClick={() => handleSort(sortKey)}
    >
      <div className="flex items-center gap-1 text-slate-500 font-bold text-xs">
        {label}
        <span className={`transition-all duration-200 ${sortConfig.key === sortKey ? 'opacity-100 translate-y-0 text-primary' : 'opacity-0 translate-y-1'}`}>
          {sortConfig.key === sortKey && sortConfig.direction === 'asc' ? <ArrowUp size={12}/> : <ArrowDown size={12}/>}
        </span>
      </div>
    </th>
  );

  // Tabs Configuration
  const tabs = [
    { id: 'all', label: 'همه پیام‌ها', icon: Inbox },
    { id: 'unread', label: 'خوانده نشده', icon: Mail },
    { id: 'pending', label: 'منتظر پاسخ', icon: Clock }, // New
    { id: 'replied', label: 'پاسخ داده شده', icon: CheckCircle2 },
  ];

  return (
    <div className="space-y-6 pb-20 p-6 min-h-screen bg-slate-50/50">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
           <h1 className="text-2xl font-black text-slate-800 flex items-center gap-3">
              <span className="w-2 h-8 bg-primary rounded-full block"></span>
              مدیریت پیام‌ها
           </h1>
           <p className="text-slate-500 text-sm mt-2 pr-4">صندوق ورودی پیام‌های "تماس با ما" سایت</p>
        </div>
        
        {/* Search Input */}
        <div className="relative w-full md:w-80 group">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-primary transition-colors" size={18} />
            <input 
              type="text" 
              placeholder="جستجو (نام، موضوع، موبایل)..." 
              className="input input-bordered w-full pr-10 bg-white shadow-sm focus:border-primary rounded-xl"
              value={searchQuery}
              onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentPage(1);
              }}
            />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar border-b border-slate-200">
         {tabs.map((tab) => (
            <button
                key={tab.id}
                onClick={() => {
                    setStatusFilter(tab.id);
                    setCurrentPage(1);
                }}
                className={`
                    flex items-center gap-2 px-4 py-3 rounded-t-xl border-b-2 transition-all text-sm font-medium whitespace-nowrap
                    ${statusFilter === tab.id 
                        ? 'border-primary text-primary bg-primary/5' 
                        : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-100'}
                `}
            >
                <tab.icon size={16} />
                {tab.label}
            </button>
         ))}
      </div>

      {/* Main Table Card */}
      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto min-h-[400px]">
          <table className="table w-full">
            <thead className="bg-slate-50/80 border-b border-slate-100 h-12">
              <tr>
                <SortableHeader label="#" sortKey="id" className="w-16" />
                <SortableHeader label="فرستنده" sortKey="full_name" />
                <SortableHeader label="موضوع" sortKey="subject" />
                <SortableHeader label="وضعیت" sortKey="status_display" className="text-center" />
                <SortableHeader label="تاریخ" sortKey="created_at" />
                <th className="text-left pl-6 text-slate-500 text-xs font-bold text-start pr-14">عملیات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {isLoading ? (
                 <tr>
                    <td colSpan="6" className="h-64 text-center text-start">
                        <span className="loading loading-spinner loading-lg text-primary"></span>
                    </td>
                 </tr>
              ) : messages.length === 0 ? (
                 <tr>
                    <td colSpan="6" className="h-80">
                        <div className="flex flex-col items-center justify-center gap-4 text-slate-300">
                            <Inbox size={64} strokeWidth={1} />
                            <span className="text-sm font-medium text-slate-400">هیچ پیامی یافت نشد</span>
                        </div>
                    </td>
                 </tr>
              ) : (
                messages.map((item) => (
                  <tr key={item.id} className={`group hover:bg-slate-50 transition-colors  ${!item.is_read ? 'bg-blue-50/30' : ''}`}>
                    <td className="font-mono text-xs text-slate-400 ">{item.id}</td>
                    
                    {/* User Info */}
                    <td className='text-start'>
                      <div className="flex items-center gap-3">
                        <div className={`avatar placeholder ${!item.is_read ? 'online' : ''}`}>
                          <div className="bg-primary text-white rounded-full w-10 h-10 ring-1 ring-slate-200 shadow-sm flex justify-center items-center ">
                             <span className="text-xs font-black">{item.full_name?.[0]}</span>
                          </div>
                        </div>
                        <div className="flex flex-col gap-0.5">
                          <span className={`text-sm ${!item.is_read ? 'font-bold text-slate-800' : 'font-medium text-slate-600'}`}>
                              {item.full_name}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono dir-ltr text-right truncate w-32">
                              {item.phone_number}
                          </span>
                        </div>
                      </div>
                    </td>

                    {/* Subject */}
                    <td className="max-w-[200px]  text-start">
                        <div className="font-medium text-slate-700 text-sm truncate" title={item.subject}>
                            {item.subject}
                        </div>
                        <div className="text-xs text-slate-400 truncate opacity-80">
                            {item.message}
                        </div>
                    </td>

                    {/* Status Badge */}
                    <td className="text-center text-start">
                        {item.admin_reply ? (
                             <div className="badge badge-success badge-sm gap-1 text-white shadow-success/20 shadow-md">
                                <CheckCircle2 size={12}/> پاسخ داده شده
                             </div>
                        ) : !item.is_read ? (
                            <div className="badge badge-error badge-sm gap-1 text-white animate-pulse">
                                <Mail size={12}/> جدید
                            </div>
                        ) : (
                            <div className="badge badge-ghost badge-sm text-slate-500">
                                <MailOpen size={12} className="mr-1"/> خوانده شده
                            </div>
                        )}
                    </td>

                    {/* Date */}
                    <td className='text-start'>
                        <div className="flex flex-col">
                            <span className="text-xs font-medium text-slate-600 font-mono">
                                {new Date(item.created_at).toLocaleDateString('fa-IR')}
                            </span>
                            <span className="text-[10px] text-slate-400 font-mono">
                                {new Date(item.created_at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                    </td>

                    {/* Actions */}
                    <td className='text-start'>
                        <div className="flex justify-end items-center gap-2 pl-2">
                            <button 
                                onClick={() => setSelectedMessage(item)}
                                className="btn btn-sm btn-ghost text-primary bg-primary/5 hover:bg-primary hover:text-white gap-2 transition-all"
                            >
                                <Eye size={16} />
                                {item.admin_reply ? 'مشاهده' : 'بررسی'}
                            </button>
                            
                            <button 
                                onClick={() => handleDelete(item.id)}
                                className="btn btn-sm btn-square btn-ghost text-slate-400 hover:text-error hover:bg-error/10 transition-colors"
                                title="حذف پیام"
                            >
                                <Trash2 size={16} />
                            </button>
                        </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        {totalPages > 0 && (
            <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
                <span className="text-xs text-slate-400">
                    نمایش {messages.length} مورد از {totalCount} پیام
                </span>
                
                <div className="join bg-white shadow-sm border border-slate-200 rounded-lg dir-ltr">
                    <button 
                        className="join-item btn btn-xs btn-ghost disabled:bg-transparent"
                        disabled={currentPage === 1}
                        onClick={() => setCurrentPage(p => p - 1)}
                    >
                        Previous
                    </button>
                    {[...Array(totalPages)].map((_, i) => (
                        <button
                            key={i}
                            className={`join-item btn btn-xs w-8 ${currentPage === i + 1 ? 'btn-primary text-white' : 'btn-ghost'}`}
                            onClick={() => setCurrentPage(i + 1)}
                        >
                            {i + 1}
                        </button>
                    ))}
                    <button 
                        className="join-item btn btn-xs btn-ghost disabled:bg-transparent"
                        disabled={currentPage === totalPages}
                        onClick={() => setCurrentPage(p => p + 1)}
                    >
                        Next
                    </button>
                </div>
            </div>
        )}
      </div>

      {/* Modal is outside the table structure */}
      <MessageReplyModal 
        isOpen={!!selectedMessage}
        message={selectedMessage}
        onClose={() => setSelectedMessage(null)}
        onSubmit={handleReplySubmit}
        isPending={replyMutation.isPending}
      />
    </div>
  );
};

export default MessageListPage;