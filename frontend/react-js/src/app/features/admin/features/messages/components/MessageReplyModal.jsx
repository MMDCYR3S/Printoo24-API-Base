// src/app/features/admin/features/messages/components/MessageReplyModal.jsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { X, Send, User, Calendar, Mail, Phone, MessageSquare } from 'lucide-react';
import { useEffect } from 'react';

// اسکیما برای اعتبارسنجی متن پاسخ
const replySchema = z.object({
  reply_text: z.string().min(10, 'متن پاسخ باید حداقل ۱۰ کاراکتر باشد'),
});

const MessageReplyModal = ({ isOpen, onClose, message, onSubmit, isPending }) => {
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(replySchema),
  });

  useEffect(() => {
    if (isOpen) reset();
  }, [isOpen, reset]);

  if (!isOpen || !message) return null;

  return (
    <dialog className="modal modal-open backdrop-blur-sm bg-slate-900/20">
      <div className="modal-box w-11/12 max-w-3xl rounded-3xl p-0 overflow-hidden bg-white shadow-2xl">
        
        {/* Header */}
        <div className="bg-slate-50 border-b border-slate-100 p-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
             <div className="bg-primary/10 text-primary p-2.5 rounded-xl">
                <MessageSquare size={20} />
             </div>
             <div>
                <h3 className="font-bold text-lg text-slate-800">جزئیات پیام</h3>
                <span className="text-xs text-slate-500 font-mono">ID: #{message.id}</span>
             </div>
          </div>
          <button onClick={onClose} className="btn btn-circle btn-ghost btn-sm">
            <X size={20} />
          </button>
        </div>

        <div className="flex flex-col md:flex-row h-[500px]">
            
            {/* Sidebar: اطلاعات کاربر */}
            <div className="w-full md:w-1/3 bg-slate-50/50 border-l border-slate-100 p-6 flex flex-col gap-6">
                <div className="flex flex-col items-center text-center">
                    <div className="avatar placeholder mb-3">
                        <div className="bg-primary text-white font-bold flex items-center justify-center rounded-full w-16 ">
                            <span className="text-xl">{message.full_name?.[0]}</span>
                        </div>
                    </div>
                    <h4 className="font-bold text-slate-700">{message.full_name}</h4>
                    <span className="text-xs text-slate-400 mt-1">کاربر مهمان</span>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center gap-3 text-sm text-slate-600">
                        <Mail size={16} className="text-primary/60"/>
                        <span className="font-mono text-xs">{message.email}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-600">
                        <Phone size={16} className="text-primary/60"/>
                        <span className="font-mono text-xs">{message.phone_number}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm text-slate-600">
                        <Calendar size={16} className="text-primary/60"/>
                        <span className="font-mono text-xs">
                            {new Date(message.created_at).toLocaleDateString('fa-IR')}
                        </span>
                    </div>
                </div>
            </div>

            {/* Main Content: متن پیام و پاسخ */}
            <div className="flex-1 p-6 flex flex-col overflow-y-auto">
                {/* موضوع و متن پیام */}
                <div className="mb-6">
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">موضوع پیام</label>
                    <div className="text-slate-800 font-bold text-lg mb-4">{message.subject}</div>
                    
                    <label className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 block">متن پیام</label>
                    <div className="bg-slate-50 p-4 rounded-2xl text-slate-600 text-sm leading-7 border border-slate-100 min-h-[100px]">
                        {message.message}
                    </div>
                </div>

                <div className="divider"></div>

                {/* فرم پاسخ */}
                <form onSubmit={handleSubmit((data) => onSubmit(message.id, data))} className="flex-1 flex flex-col">
                    <label className="text-xs font-bold text-primary uppercase tracking-wider mb-2 block flex items-center gap-2">
                        <Send size={14}/> پاسخ شما (ارسال ایمیل)
                    </label>
                    <textarea 
                        {...register('reply_text')}
                        className={`textarea textarea-bordered w-full flex-1 rounded-2xl resize-none focus:border-primary ${errors.reply_text ? 'textarea-error' : ''}`}
                        placeholder="متن پاسخ خود را اینجا بنویسید..."
                    ></textarea>
                    {errors.reply_text && <span className="text-error text-xs mt-2">{errors.reply_text.message}</span>}

                    <div className="mt-4 flex justify-end gap-3">
                        <button type="button" onClick={onClose} className="btn btn-ghost">انصراف</button>
                        <button type="submit" className="btn btn-primary px-8 rounded-xl shadow-lg shadow-primary/20" disabled={isPending}>
                            {isPending ? <span className="loading loading-spinner"></span> : 'ارسال پاسخ'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
      </div>
    </dialog>
  );
};

export default MessageReplyModal;