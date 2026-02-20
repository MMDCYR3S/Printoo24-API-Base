import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowRight, Download, FileText, Layers, MapPin, 
  User, Package, DollarSign, Calendar, Info , Printer , FileCheck
} from 'lucide-react';
import { profileService } from '../../services/profileService';
import { formatCurrency } from '../../utils/formatters';

import pageText from '../../lang/pages.json'
import globalText from '../../lang/global.json'

// --- Configuration & Constants ---
const STATUS_MAP = {
  7:  { label: pageText.profile.orderDetailPage.statuses.s7, color: "badge-warning", bg: "bg-warning/10" },
  8:  { label: pageText.profile.orderDetailPage.statuses.s8, color: "badge-info", bg: "bg-info/10" },
  9:  { label: pageText.profile.orderDetailPage.statuses.s9, color: "badge-error", bg: "bg-error/10" },
  10: { label: pageText.profile.orderDetailPage.statuses.s10, color: "badge-info", bg: "bg-info/10" },
  11: { label: pageText.profile.orderDetailPage.statuses.s11, color: "badge-error", bg: "bg-error/10" },
  12: { label: pageText.profile.orderDetailPage.statuses.s12, color: "badge-primary", bg: "bg-primary/10" },
  13: { label: pageText.profile.orderDetailPage.statuses.s13, color: "badge-success", bg: "bg-success/10" },
  14: { label: pageText.profile.orderDetailPage.statuses.s14, color: "badge-error", bg: "bg-error/10" },
  15: { label: pageText.profile.orderDetailPage.statuses.s15, color: "badge-success", bg: "bg-success/10" },
  16: { label: pageText.profile.orderDetailPage.statuses.s16, color: "badge-ghost", bg: "bg-slate-100" },
};

const SPEC_LABELS = {
  size: pageText.profile.orderDetailPage.specLabels.size,
  paper: pageText.profile.orderDetailPage.specLabels.paper,
  coating: pageText.profile.orderDetailPage.specLabels.coating,
  cutting: pageText.profile.orderDetailPage.specLabels.cutting,
  quantity: pageText.profile.orderDetailPage.specLabels.quantity,
  color_mode: pageText.profile.orderDetailPage.specLabels.color_mode,
  print_side: pageText.profile.orderDetailPage.specLabels.print_side,
  category: pageText.profile.orderDetailPage.specLabels.category
};

// --- Sub-Components ---

const SpecBadge = ({ label, value }) => (
  <div className="flex items-center gap-2 bg-slate-50 border border-slate-100 px-3 py-1.5 rounded-xl">
    <span className="text-[10px] text-slate-400 font-bold">{SPEC_LABELS[label] || label}:</span>
    <span className="text-xs text-slate-700 font-medium">{value}</span>
  </div>
);

const OrderDetailPage = () => {
  const { id } = useParams();
  
  const { data: order, isLoading, isError } = useQuery({
    queryKey: ['order-detail', id],
    queryFn: () => profileService.getOrderDetails(id),
  });

  if (isLoading) return (
    <div className="flex justify-center items-center min-h-[400px]">
      <span className="loading loading-spinner text-primary loading-lg"></span>
    </div>
  );

  if (isError || !order) return (
    <div className="alert alert-error shadow-lg max-w-2xl mx-auto mt-10">
      <Info />
      <span>{pageText.profile.orderDetailPage.errorGettingOrder}</span>
    </div>
  );

  const statusInfo = STATUS_MAP[order.current_status] || { label: pageText.profile.orderDetailPage.unknown, color: "badge-ghost" };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-500">
      {/* 1. Navigation & Basic Info */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-6">
        <div className="flex items-center gap-4">
          <Link to="/profile/orders" className="btn btn-circle btn-ghost bg-white shadow-sm border-slate-200">
            <ArrowRight size={22} className="text-slate-600"/>
          </Link>
          <div>
            <h1 className="text-2xl font-black text-slate-800 tracking-tight">
              {pageText.profile.orderDetailPage.orderDetail} <span className="text-primary">#{order.order_code}</span>
            </h1>
            <p className="text-slate-400 text-sm flex items-center gap-1.5 mt-1">
              <Calendar size={14} />
              {pageText.profile.orderDetailPage.registeredAt} {new Date(order.created_at).toLocaleDateString('fa-IR')}
            </p>
          </div>
        </div>
        <div className={`px-6 py-3 rounded-2xl border-2 flex items-center gap-3 ${statusInfo.bg} ${statusInfo.color.replace('badge-', 'border-')}`}>

<Link to={`/profile/orders/${id}/quotation`} className="btn btn-outline btn-sm h-12 px-4 rounded-2xl border-slate-200 text-slate-600 hover:text-primary hover:border-primary hover:bg-primary/5">
      <Printer size={16} className="ml-1" />
      {pageText.profile.orderDetailPage.quotation}
    </Link>
    <Link to={`/profile/orders/${id}/invoice`} className="btn btn-outline bg-white btn-sm h-10 px-4 rounded-xl border-slate-200 text-slate-600 hover:text-success hover:border-success hover:bg-success/5 flex-1 md:flex-none">
              <FileCheck size={16} className="ml-1" />
              {pageText.profile.orderDetailPage.invoice}
            </Link>

          <div className={`w-2.5 h-2.5 rounded-full animate-pulse ${statusInfo.color.replace('badge-', 'bg-')}`}></div>
          <span className="font-bold text-slate-800">{statusInfo.label}</span>
        </div>
      </header>

      {/* 2. Overview Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Total Price Card */}
        <div className="bg-white p-6 rounded-[2.5rem] border border-slate-100 shadow-sm flex flex-col items-center justify-center text-center space-y-2">
          <div className="p-3 bg-primary/10 rounded-2xl text-primary">
            <DollarSign size={24} />
          </div>
          <span className="text-slate-400 text-xs font-bold uppercase tracking-widest">{pageText.profile.OrderDetailPage.totalPrice}</span>
          <div className="text-3xl font-black text-slate-800">
            {formatCurrency(order.total_price)} <span className="text-sm font-medium text-slate-400">{globalText.currency}</span>
          </div>
        </div>

        {/* Shipping Address Card */}
        <div className="bg-white p-6 rounded-[2.5rem] border border-slate-100 shadow-sm lg:col-span-2 space-y-4">
          <div className="flex items-center gap-2 text-slate-800 font-bold border-b border-slate-50 pb-3">
            <MapPin size={18} className="text-primary" />
            {pageText.profile.orderDetailPage.receiverInfo}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-y-4 gap-x-8">
            <div className="flex flex-col gap-1">
              <span className="text-[10px] text-slate-400 font-bold">{pageText.profile.orderDetailPage.receiver}</span>
              <span className="text-sm font-semibold flex items-center gap-2"><User size={14} className="text-slate-300"/> {pageText.profile.orderDetailPage.userCountOf} {order.user}</span>
            </div>
            <div className="flex flex-col gap-1 md:col-span-2 bg-slate-50 p-4 rounded-2xl">
              <span className="text-[10px] text-slate-400 font-bold mb-1">{pageText.profile.OrderDetailPage.fullAddress}</span>
              <p className="text-sm text-slate-600 leading-relaxed">{order.full_address}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Items List */}
      <section className="space-y-6">
        <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2 px-2">
          <Layers size={20} className="text-primary" />
          {pageText.profile.orderDetailPage.orderItemList} ({order.order_item?.length})
        </h2>

        {order.order_item?.map((item) => (
          <div key={item.id} className="group bg-white rounded-[2.5rem] border border-slate-200 overflow-hidden hover:shadow-xl hover:shadow-slate-200/50 transition-all duration-300">
            {/* Item Header */}
            <div className="bg-slate-50/50 p-6 border-b border-slate-100 flex flex-wrap justify-between items-center gap-4 group-hover:bg-slate-50 transition-colors">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-white rounded-2xl shadow-sm flex items-center justify-center text-primary border border-slate-100">
                  <Package size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-slate-800">{pageText.profile.orderDetailPage.specialProduct} #{item.id}</h3>
                  <p className="text-xs text-slate-400 mt-0.5 font-medium">{pageText.profile.orderDetailPage.count} {item.quantity.toLocaleString()} {pageText.profile.orderDetailPage.number}</p>
                </div>
              </div>
              <div className="bg-primary px-4 py-2 rounded-xl text-white font-bold text-sm shadow-lg shadow-primary/20">
                {formatCurrency(item.item_price)} {globalText.currency}
              </div>
            </div>

            {/* Item Content */}
            <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Specs */}
              <div>
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                  <div className="w-1 h-3 bg-primary rounded-full"></div>
                  {pageText.profile.orderDetailPage.productionTechnicalInfo}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {item.specs?.specifications && Object.entries(item.specs.specifications).map(([key, value]) => (
                    <SpecBadge key={key} label={key} value={value} />
                  ))}
                </div>
                
                {item.specs?.admin_logs?.length > 0 && (
                  <div className="mt-6 p-4 bg-orange-50 rounded-2xl border border-orange-100">
                    <span className="text-[10px] font-bold text-orange-400 block mb-2">{pageText.profile.orderDetailPage.systemNotes}</span>
                    {item.specs.admin_logs.map((log, idx) => (
                      <p key={idx} className="text-xs text-orange-700 leading-relaxed">• {log}</p>
                    ))}
                  </div>
                )}
              </div>

              {/* Files */}
              <div className="space-y-4">
                <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                  <div className="w-1 h-3 bg-blue-500 rounded-full"></div>
                  {pageText.profile.orderDetailPage.sendingDesignFiles}
                </h4>
                <div className="grid grid-cols-1 gap-3">
                  {item.design_files?.length > 0 ? (
                    item.design_files.map((file) => (
                      <a 
                        key={file.id} 
                        href={file.file_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="flex items-center justify-between p-4 rounded-2xl bg-slate-50 border border-slate-100 hover:border-primary hover:bg-white hover:shadow-md transition-all group/file"
                      >
                        <div className="flex items-center gap-3 overflow-hidden">
                          <div className="p-2 bg-white rounded-lg text-slate-400 group-hover/file:text-primary transition-colors">
                            <FileText size={20} />
                          </div>
                          <span className="text-xs font-bold text-slate-700 truncate">{pageText.profile.orderDetailPage.lookDesignFiles} #{file.id}</span>
                        </div>
                        <Download size={18} className="text-slate-300 group-hover/file:text-primary" />
                      </a>
                    ))
                  ) : (
                    <div className="text-center py-8 bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                      <p className="text-xs text-slate-400 font-medium">{pageText.profile.orderDetailPage.fileDidNotFound}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
};

export default OrderDetailPage;