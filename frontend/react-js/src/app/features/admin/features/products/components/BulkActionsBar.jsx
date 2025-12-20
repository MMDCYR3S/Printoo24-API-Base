// src/app/features/admin/products/components/BulkActionsBar.jsx
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, ShieldCheck, ShieldBan, X, Layers } from 'lucide-react';

const BulkActionsBar = ({ selectedCount, onClear, onDelete, onStatusChange }) => {
  return (
    <AnimatePresence>
      {selectedCount > 0 && (
        <motion.div 
          initial={{ y: 100, opacity: 0, scale: 0.95 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          exit={{ y: 100, opacity: 0, scale: 0.95 }}
          transition={{ type: "spring", stiffness: 400, damping: 30 }}
          className="fixed bottom-6 left-0 right-0 mx-auto w-fit z-[60] flex items-center gap-3 bg-slate-900/90 text-white pl-3 pr-5 py-3 rounded-full shadow-2xl shadow-slate-900/40 border border-white/10 backdrop-blur-md"
        >
          <div className="flex items-center gap-3 border-r border-white/10 pr-3 ml-1">
            <span className="bg-primary text-white text-xs font-bold px-2 py-1 rounded-md min-w-[24px] text-center">
              {selectedCount}
            </span>
            <span className="text-sm font-medium hidden sm:inline text-slate-200">انتخاب شده</span>
          </div>

          <div className="flex items-center gap-1">
            <button 
                onClick={() => onStatusChange(true)}
                className="btn btn-ghost btn-sm btn-circle text-emerald-400 hover:bg-white/10 tooltip tooltip-top"
                data-tip="فعال‌سازی"
            >
                <ShieldCheck size={20}/>
            </button>
            
            <button 
                onClick={() => onStatusChange(false)}
                className="btn btn-ghost btn-sm btn-circle text-amber-400 hover:bg-white/10 tooltip tooltip-top"
                data-tip="غیرفعال‌سازی"
            >
                <ShieldBan size={20}/>
            </button>
            
            <button 
                onClick={onDelete}
                className="btn btn-ghost btn-sm btn-circle text-red-400 hover:bg-red-500/20 tooltip tooltip-top"
                data-tip="حذف انتخاب‌ها"
            >
                <Trash2 size={20}/>
            </button>
          </div>

          <div className="w-px h-5 bg-white/10 mx-1"></div>

          <button 
            onClick={onClear}
            className="btn btn-circle btn-xs btn-ghost text-white/40 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X size={16} />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default BulkActionsBar;