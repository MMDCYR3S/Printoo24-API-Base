import React, { useState } from 'react';
import { 
  User, Package, CheckCircle, Search, Plus, Trash2, 
  ChevronLeft, ChevronRight, ShoppingCart 
} from 'lucide-react';
import { useOrderCreate } from '../../hooks/useOrderCreate';
import { useCustomers } from '../../hooks/useCustomers';
import { useAdminProducts } from '../../hooks/useAdminProducts'; 
import { formatPrice } from '../../utils/formatPrice';
import { MapPin } from 'lucide-react';

const OrderCreatePage = () => {
  const { 
    step, totalSteps, nextStep, prevStep, 
    selectedUser, setSelectedUser, 
    cartItems, setCartItems, 
    submitOrder, isSubmitting, calculateTotal , userDetails,          
    selectedAddressId,    
    setSelectedAddressId  
  } = useOrderCreate();

  return (
    <div className="p-6 max-w-5xl mx-auto pb-24">
      <h1 className="text-2xl font-black text-slate-800 mb-8">ثبت سفارش جدید</h1>

      <ul className="steps w-full mb-10">
        <li className={`step ${step >= 1 ? 'step-primary' : ''}`}>انتخاب مشتری</li>
        <li className={`step ${step >= 2 ? 'step-primary' : ''}`}>افزودن محصولات</li>
        <li className={`step ${step >= 3 ? 'step-primary' : ''}`}>تایید و ثبت</li>
      </ul>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm min-h-[400px] p-6 relative">
        
        {step === 1 && (
          <StepCustomerSelection 
            selectedUser={selectedUser} 
            onSelect={setSelectedUser}
            userDetails={userDetails}             
            selectedAddressId={selectedAddressId} 
            onSelectAddress={setSelectedAddressId} 
          />
        )}

        {step === 2 && <StepProductSelection cartItems={cartItems} setCartItems={setCartItems} />}

        {step === 3 && (
          <div className="text-center space-y-6 py-10">
            <CheckCircle size={64} className="text-emerald-500 mx-auto" />
            <div className="space-y-2">
              <h3 className="text-xl font-bold">آماده ثبت نهایی</h3>
              <p className="text-slate-500">
                سفارش برای <span className="font-bold text-slate-800">{selectedUser?.first_name} {selectedUser?.last_name}</span> 
                با مبلغ کل <span className="font-bold text-emerald-600 dir-ltr">{formatPrice(calculateTotal())}</span> ثبت خواهد شد.
              </p>
            </div>
            
            <div className="max-w-md mx-auto bg-slate-50 rounded-xl p-4 text-sm text-slate-600 text-right">
              <ul className="list-disc list-inside space-y-1">
                {cartItems.map((item, idx) => (
                  <li key={idx}>
                    {item.quantity} عدد {item.product.name} 
                    {item.width ? ` (${item.width}x${item.height})` : ''}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

      </div>

      <div className="flex justify-between mt-6">
        <button 
          onClick={prevStep} 
          disabled={step === 1}
          className="btn btn-ghost gap-2"
        >
          <ChevronRight size={20}/> مرحله قبل
        </button>

        {step < totalSteps ? (
          <button onClick={nextStep} className="btn btn-primary gap-2 px-8">
            مرحله بعد <ChevronLeft size={20}/>
          </button>
        ) : (
          <button 
            onClick={submitOrder} 
            disabled={isSubmitting}
            className="btn btn-success text-white gap-2 px-8 shadow-lg shadow-success/30"
          >
            {isSubmitting ? <span className="loading loading-spinner"></span> : <><CheckCircle size={20}/> ثبت نهایی سفارش</>}
          </button>
        )}
      </div>
    </div>
  );
};

// --- Sub-Components ---

const StepCustomerSelection = ({ selectedUser, onSelect, userDetails, selectedAddressId, onSelectAddress }) => {
  const [term, setTerm] = useState('');
  const { usersQuery } = useCustomers();
  
  const filteredUsers = usersQuery.data?.filter(u => 
    u.username.includes(term) || u.phone_number?.includes(term) || u.first_name?.includes(term)
  ) || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      
      <div className="space-y-4">
        <h3 className="font-bold border-b pb-2">۱. انتخاب مشتری</h3>
        <div className="form-control relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            className="input input-bordered w-full pl-10" 
            placeholder="جستجوی مشتری (نام، موبایل)..."
            value={term}
            onChange={e => setTerm(e.target.value)}
          />
        </div>
        <div className="max-h-60 overflow-y-auto border rounded-xl divide-y bg-slate-50">
          {filteredUsers.map(user => (
            <div 
              key={user.id} 
              onClick={() => onSelect(user)}
              className={`p-3 cursor-pointer hover:bg-white flex justify-between items-center transition-colors ${selectedUser?.id === user.id ? 'bg-primary/10 border-r-4 border-primary' : ''}`}
            >
              <div className="text-sm">
                <div className="font-bold">{user.first_name || user.username}</div>
                <div className="text-xs text-slate-400">{user.phone_number}</div>
              </div>
              {selectedUser?.id === user.id && <CheckCircle size={16} className="text-primary"/>}
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="font-bold border-b pb-2 opacity-50" style={{ opacity: selectedUser ? 1 : 0.5 }}>
          ۲. انتخاب آدرس ارسال
        </h3>
        
        {!selectedUser ? (
          <div className="text-slate-400 text-sm text-center py-10 bg-slate-50 rounded-xl border border-dashed">
            ابتدا مشتری را انتخاب کنید
          </div>
        ) : (
          <div className="space-y-2">
            {!userDetails ? (
              <div className="loading loading-spinner text-primary mx-auto block"></div>
            ) : userDetails.addresses && userDetails.addresses.length > 0 ? (
              userDetails.addresses.map((addr) => (
                <div 
                  key={addr.id}
                  onClick={() => onSelectAddress(addr.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${selectedAddressId === addr.id ? 'border-primary bg-primary/5 ring-1 ring-primary' : 'border-slate-200 hover:border-slate-300'}`}
                >
                  <div className="flex items-start gap-3">
                    <MapPin size={18} className={selectedAddressId === addr.id ? "text-primary" : "text-slate-400"} />
                    <div className="text-sm">
                      <p className="font-medium text-slate-800 leading-snug">{addr.detail || addr.address}</p>
                      <p className="text-xs text-slate-500 mt-1">{addr.city} - {addr.postal_code}</p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="alert alert-warning text-sm">
                <span>⚠️ این کاربر هیچ آدرسی ثبت نکرده است!</span>
              </div>
            )}
          </div>
        )}
      </div>

    </div>
  );
};

const StepProductSelection = ({ cartItems, setCartItems }) => {
  const { allProducts, isLoading } = useAdminProducts(); 
  const [selectedProduct, setSelectedProduct] = useState(null);
  
  // استیت جستجوی محصول
  const [searchTerm, setSearchTerm] = useState('');
  
  const [qty, setQty] = useState(1);
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');

  // فیلتر کردن محصولات بر اساس جستجو
  const filteredProducts = allProducts?.filter(p => 
    p.name?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleAddItem = () => {
    if (!selectedProduct) return;
    const newItem = {
      product: selectedProduct,
      quantity: qty,
      width: width || 0,
      height: height || 0,
      price: selectedProduct.price
    };
    setCartItems([...cartItems, newItem]);
    
    setSelectedProduct(null);
    setSearchTerm('');
    setQty(1);
    setWidth('');
    setHeight('');
  };

  const handleRemoveItem = (idx) => {
    setCartItems(cartItems.filter((_, i) => i !== idx));
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      
      {/* فرم افزودن محصول */}
      <div className="space-y-4 border-l pl-6 border-slate-100">
        <h3 className="font-bold flex items-center gap-2"><Plus size={18}/> افزودن محصول</h3>
        
        {/* اینپوت جستجوی محصول مستقیم */}
        <div className="form-control relative">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            className="input input-bordered w-full pl-10" 
            placeholder="جستجوی نام محصول..."
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            disabled={isLoading}
          />
        </div>

        {/* لیست محصولات مشابه لیست مشتریان */}
        <div className="max-h-48 overflow-y-auto border rounded-xl divide-y bg-slate-50">
          {isLoading ? (
            <div className="p-4 text-center text-sm text-slate-400">در حال دریافت محصولات...</div>
          ) : filteredProducts.length === 0 ? (
            <div className="p-4 text-center text-sm text-slate-400">محصولی یافت نشد</div>
          ) : (
            filteredProducts.map(p => (
              <div 
                key={p.id} 
                onClick={() => setSelectedProduct(p)}
                className={`p-3 cursor-pointer hover:bg-white flex justify-between items-center transition-colors ${selectedProduct?.id === p.id ? 'bg-primary/10 border-r-4 border-primary' : ''}`}
              >
                <div className="text-sm font-bold text-slate-700">{p.name}</div>
                <div className="text-xs text-slate-500 dir-ltr bg-slate-100 px-2 py-1 rounded">
                  {new Intl.NumberFormat('fa-IQ').format(p.price)} IQD
                </div>
              </div>
            ))
          )}
        </div>

        {selectedProduct && (
          <div className="grid grid-cols-3 gap-2 bg-slate-50 border border-primary/20 p-3 rounded-xl animate-in fade-in slide-in-from-top-2">
            <div className="form-control">
              <label className="label text-[10px]">تعداد</label>
              <input 
                type="number" 
                className="input input-sm input-bordered text-center focus:border-primary" 
                value={qty} 
                onChange={e => setQty(Number(e.target.value))}
                min={1}
              />
            </div>
            <div className="form-control">
              <label className="label text-[10px]">عرض (cm)</label>
              <input type="number" className="input input-sm input-bordered text-center focus:border-primary" value={width} onChange={e => setWidth(Number(e.target.value))} placeholder="اختیاری"/>
            </div>
            <div className="form-control">
              <label className="label text-[10px]">ارتفاع (cm)</label>
              <input type="number" className="input input-sm input-bordered text-center focus:border-primary" value={height} onChange={e => setHeight(Number(e.target.value))} placeholder="اختیاری"/>
            </div>
          </div>
        )}

        <button 
          onClick={handleAddItem} 
          disabled={!selectedProduct}
          className="btn btn-primary w-full btn-sm shadow-lg shadow-primary/30"
        >
          افزودن به لیست
        </button>
      </div>

      {/* لیست اقلام انتخاب شده */}
      <div className="space-y-3">
        <h3 className="font-bold flex items-center gap-2 text-slate-700"><ShoppingCart size={18}/> اقلام انتخاب شده</h3>
        {cartItems.length === 0 ? (
          <div className="text-center py-10 text-slate-400 bg-slate-50 rounded-xl border border-dashed border-slate-200">
            هنوز آیتمی اضافه نشده است
          </div>
        ) : (
          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
            {cartItems.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center bg-white border border-slate-200 p-3 rounded-xl shadow-sm">
                <div className="text-sm">
                  <div className="font-bold text-slate-800">{item.product.name}</div>
                  <div className="text-xs text-slate-500 mt-1">
                    <span className="bg-slate-100 px-2 py-0.5 rounded">{item.quantity} عدد</span>
                    {item.width ? <span className="mr-2">| {item.width}x{item.height} cm</span> : ''}
                  </div>
                </div>
                <button onClick={() => handleRemoveItem(idx)} className="btn btn-ghost btn-xs text-error hover:bg-error/10 btn-square">
                  <Trash2 size={16}/>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderCreatePage;