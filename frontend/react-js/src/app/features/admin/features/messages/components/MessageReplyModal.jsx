// src/app/features/admin/features/messages/components/MessageReplyModal.jsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Send, User, Calendar, Mail, Phone, CheckCircle2, Clock } from 'lucide-react';
import { useEffect } from 'react';

const replySchema = z.object({
  reply_text: z.string().min(5, 'متن پاسخ خیلی کوتاه است'),
});

const MessageReplyModal = ({ isOpen, onClose, message, onSubmit, isPending }) => {
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(replySchema),
  });

  useEffect(() => {
    if (isOpen) reset();
  }, [isOpen, reset]);

  if (!isOpen || !message) return null;

  const isReplied = !!message.admin_reply;

  return (
    <dialog className="modal modal-open backdrop-blur-md bg-slate-900/30 z-50">
      <div className="modal-box w-11/12 max-w-4xl rounded-3xl p-0 overflow-hidden bg-white shadow-2xl flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="bg-white border-b border-slate-100 p-5 flex justify-between items-center sticky top-0 z-10">
          <div className="flex items-center gap-3">
             <div className={`p-2.5 rounded-xl ${isReplied ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'}`}>
                {isReplied ? <CheckCircle2 size={22} /> : <Clock size={22} />}
             </div>
             <div>
                <h3 className="font-bold text-lg text-slate-800">
                    {isReplied ? 'جزئیات پاسخ ارسال شده' : 'پاسخ به پیام کاربر'}
                </h3>
                <span className="text-xs text-slate-500 font-mono">Message ID: #{message.id}</span>
             </div>
          </div>
          <button onClick={onClose} className="btn btn-circle btn-ghost btn-sm text-slate-400 hover:text-slate-800">
            <X size={20} />
          </button>
        </div>

        <div className="flex flex-col lg:flex-row flex-1 overflow-hidden">
            
            {/* Sidebar: Sender Info */}
            <div className="w-full lg:w-80 bg-slate-50 border-l border-slate-100 p-6 overflow-y-auto">
                <div className="flex flex-col items-center text-center mb-6">
                    <div className="avatar placeholder mb-3">
                        <div className="bg-white border border-slate-200 text-slate-700 rounded-full w-20 shadow-sm flex justify-center items-center">
                            <span className="text-3xl font-black">{message.full_name?.[0]}</span>
                        </div>
                    </div>
                    <h4 className="font-bold text-slate-800 text-lg">{message.full_name}</h4>
                    <span className="badge badge-ghost badge-sm mt-2 font-mono text-[10px]">{message.status_display}</span>
                </div>

                <div className="space-y-4 bg-white p-4 rounded-2xl border border-slate-100 shadow-sm">
                    <InfoItem icon={Mail} label="ایمیل" value={message.email} copyable />
                    <InfoItem icon={Phone} label="موبایل" value={message.phone_number} copyable />
                    <InfoItem icon={Calendar} label="تاریخ ارسال" value={new Date(message.created_at).toLocaleDateString('fa-IR')} />
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-6 bg-white">
                
                {/* User Message Bubble */}
                <div>
                    <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 mr-2">پیام کاربر</div>
                    <div className="chat chat-start w-full">
                        <div className="chat-bubble chat-bubble-ghost bg-slate-100 text-slate-700 w-full max-w-full rounded-2xl p-5 shadow-sm border border-slate-200/50">
                            <h5 className="font-bold text-slate-900 mb-2 border-b border-slate-200 pb-2 border-dashed">{message.subject}</h5>
                            <p className="leading-7 whitespace-pre-wrap text-sm">{message.message}</p>
                        </div>
                    </div>
                </div>

                {isReplied ? (
                    /* Admin Reply (Read Only) */
                    <div>
                        <div className="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-2 mr-2 flex items-center gap-1">
                            <CheckCircle2 size={12}/> پاسخ داده شده در {new Date(message.replied_at).toLocaleDateString('fa-IR')}
                        </div>
                        <div className="chat chat-start w-full">
                            <div className="chat-bubble bg-emerald-50 text-slate-800 w-full max-w-full rounded-2xl p-5 border border-emerald-100 shadow-sm">
                                <p className="leading-7 whitespace-pre-wrap text-sm">{message.admin_reply}</p>
                            </div>
                        </div>
                        <div className="mt-8 flex justify-end">
                            <button onClick={onClose} className="btn btn-outline w-32">بستن</button>
                        </div>
                    </div>
                ) : (
                    /* Reply Form */
                    <form onSubmit={handleSubmit((data) => onSubmit(message.id, data))} className="flex flex-col flex-1 mt-4">
                        <div className="text-xs font-bold text-primary uppercase tracking-wider mb-2 mr-2">ارسال پاسخ جدید</div>
                        <div className="relative flex-1">
                            <textarea 
                                {...register('reply_text')}
                                className={`textarea textarea-bordered w-full h-40 rounded-2xl text-sm leading-6 focus:border-primary focus:ring-1 focus:ring-primary/20 transition-all ${errors.reply_text ? 'textarea-error' : ''}`}
                                placeholder="پاسخ شما به ایمیل کاربر ارسال خواهد شد..."
                            ></textarea>
                            <div className="absolute bottom-3 left-3 flex gap-2">
                                <button type="button" onClick={onClose} className="btn btn-sm btn-ghost text-slate-500">لغو</button>
                                <button type="submit" className="btn btn-sm btn-primary gap-2 shadow-lg shadow-primary/20" disabled={isPending}>
                                    {isPending ? <span className="loading loading-spinner loading-xs"></span> : <><Send size={14}/> ارسال</>}
                                </button>
                            </div>
                        </div>
                        {errors.reply_text && <span className="text-error text-xs mt-2 mr-1">{errors.reply_text.message}</span>}
                    </form>
                )}
            </div>
        </div>
      </div>
    </dialog>
  );
};

// Helper Component for Sidebar Info
const InfoItem = ({ icon: Icon, label, value, copyable }) => (
    <div className="flex flex-col gap-1">
        <div className="flex items-center gap-1 text-slate-400 text-[10px]">
            <Icon size={12} /> <span>{label}</span>
        </div>
        <div 
            className={`font-mono text-xs text-slate-700 dir-ltr text-right truncate ${copyable ? 'cursor-pointer hover:text-primary transition-colors' : ''}`}
            onClick={() => {
                if(copyable) {
                    navigator.clipboard.writeText(value);
                    // Toast could be added here
                }
            }}
        >
            {value}
        </div>
    </div>
);

export default MessageReplyModal;