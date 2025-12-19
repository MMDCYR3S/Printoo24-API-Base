// src/app/features/admin/customers/components/BulkActionsBar.jsx
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, ShieldCheck, ShieldBan, X } from 'lucide-react';

const BulkActionsBar = ({ selectedCount, onClear, onDelete, onStatusChange }) => {
  return (
    <AnimatePresence>
      {selectedCount > 0 && (
        <motion.div 
          initial={{ y: 100, opacity: 0, scale: 0.9 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          exit={{ y: 100, opacity: 0, scale: 0.9 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[50] flex items-center gap-4 bg-slate-900 text-white pl-3 pr-6 py-3 rounded-2xl shadow-2xl shadow-slate-900/30 border border-slate-700/50 backdrop-blur-md"
        >
          <div className="flex items-center gap-3 border-l border-white/10 pl-4">
            <div className="badge badge-primary font-bold">{selectedCount}</div>
            <span className="text-sm font-medium">مورد انتخاب شد</span>
          </div>

          <div className="flex items-center gap-1">
            <button 
                onClick={() => onStatusChange(true)}
                className="btn btn-ghost btn-sm text-emerald-400 hover:bg-white/10 gap-2 font-normal"
            >
                <ShieldCheck size={18}/>
                <span className="hidden sm:inline">فعال‌سازی</span>
            </button>
            
            <button 
                onClick={() => onStatusChange(false)}
                className="btn btn-ghost btn-sm text-amber-400 hover:bg-white/10 gap-2 font-normal"
            >
                <ShieldBan size={18}/>
                <span className="hidden sm:inline">مسدودسازی</span>
            </button>
            
            <button 
                onClick={onDelete}
                className="btn btn-ghost btn-sm text-red-400 hover:bg-red-500/20 hover:text-red-300 gap-2 font-normal"
            >
                <Trash2 size={18}/>
                <span className="hidden sm:inline">حذف</span>
            </button>
          </div>

          <button 
            onClick={onClear}
            className="btn btn-circle btn-xs btn-ghost text-white/40 hover:text-white hover:bg-white/10 transition-colors mr-2"
          >
            <X size={16} />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default BulkActionsBar;