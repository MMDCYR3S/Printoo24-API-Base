import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapPin, User, Phone, CheckCircle, CreditCard, Plus, Home } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { cartService } from '../../services/cartService';
import { locationService } from '../../services/locationService';
import { orderService } from '../../services/orderService';
import clsx from 'clsx';

// وارد کردن فایل‌های ترجمه
import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const CheckoutPage = () => {
  const navigate = useNavigate();
  
  // --- State ---
  const [cartSummary, setCartSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  // دیتای لوکیشن
  const [addresses, setAddresses] = useState([]); // لیست آدرس‌های سرور
  const [provinces, setProvinces] = useState([]);
  const [cities, setCities] = useState([]);

  // حالت انتخاب آدرس: 'existing' | 'new'
  const [addressMode, setAddressMode] = useState('new'); 
  const [selectedAddressId, setSelectedAddressId] = useState(null);

  // فرم دیتا
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    // فیلدهای آدرس جدید
    province_id: '',
    city_id: '',
    address_text: '',
    postal_code: ''
  });

  // --- Initial Data Fetching ---
  useEffect(() => {
    const initData = async () => {
      try {
        setLoading(true);
        // 1. سبد خرید
        const cart = await cartService.getCartItems();
        if (!cart?.items?.length) {
          navigate('/cart');
          return;
        }
        setCartSummary(cart);

        // 2. آدرس‌های کاربر
        try {
          const userAddresses = await orderService.getAddresses();
          setAddresses(userAddresses || []);
          
          // اگر آدرس داشت، اولی را پیش‌فرض انتخاب کن
          if (userAddresses && userAddresses.length > 0) {
            setAddressMode('existing');
            setSelectedAddressId(userAddresses[0].id);
          } else {
            setAddressMode('new');
          }
        } catch (addrErr) {
          console.warn("Address fetch failed (maybe guest):", addrErr);
          setAddressMode('new');
        }

        // 3. لیست استان‌ها (برای فرم آدرس جدید)
        const provs = await locationService.getProvinces();
        setProvinces(provs || []);

      } catch (err) {
        console.error(err);
        toast.error(pageText.checkout.fetchError);
      } finally {
        setLoading(false);
      }
    };

    initData();
  }, [navigate]);

  // --- Handlers ---
  
  const handleProvinceChange = async (e) => {
    const provId = e.target.value;
    setFormData(prev => ({ ...prev, province_id: provId, city_id: '' }));
    
    if (provId) {
      try {
        const citiesData = await locationService.getCities(provId);
        setCities(citiesData || []);
      } catch (err) {
        console.error(err);
      }
    } else {
      setCities([]);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
        const payload = {};

        // الف) افزودن نام و تلفن (اگر پر شده باشند)
        if (formData.first_name) payload.first_name = formData.first_name;
        if (formData.last_name) payload.last_name = formData.last_name;
        if (formData.phone_number) payload.phone_number = formData.phone_number;

        // ب) افزودن آدرس
        if (addressMode === 'existing') {
            // پیدا کردن آدرس انتخاب شده از لیست
            const selectedAddr = addresses.find(a => a.id === selectedAddressId);
            if (!selectedAddr) {
                toast.error(pageText.checkout.invalidAddress);
                setSubmitting(false);
                return;
            }
            // استخراج فیلدها برای ارسال به API (چون API آیدی آدرس نمی‌گیرد، بلکه جزئیات می‌خواهد)
            payload.province_id = selectedAddr.province?.id || selectedAddr.province;
            payload.city_id = selectedAddr.city?.id || selectedAddr.city;
            payload.address_text = selectedAddr.address;
            payload.postal_code = selectedAddr.postal_code;
        } else {
            // حالت آدرس جدید
            if (!formData.province_id || !formData.city_id || !formData.address_text) {
                toast.error(pageText.checkout.fillRequiredFields);
                setSubmitting(false);
                return;
            }
            payload.province_id = parseInt(formData.province_id);
            payload.city_id = parseInt(formData.city_id);
            payload.address_text = formData.address_text;
            if (formData.postal_code) payload.postal_code = formData.postal_code;
        }

        // ارسال به سرور
        await orderService.checkout(payload);
        
        toast.success(pageText.checkout.orderSuccess);
        navigate('/profile/orders'); // هدایت به لیست سفارشات

    } catch (err) {
        console.error("Checkout Error:", err);
        const msg = err.response?.data?.detail || pageText.checkout.orderSubmitError;
        toast.error(msg);
    } finally {
        setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><span className="loading loading-spinner loading-lg text-primary"></span></div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="container mx-auto max-w-6xl">
        
        <h1 className="text-3xl font-black text-slate-800 mb-8 flex items-center gap-3">
          <CheckCircle className="text-emerald-500" />
          {pageText.checkout.pageTitle}
        </h1>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* --- ستون راست: فرم‌ها --- */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* ۱. مشخصات گیرنده (اختیاری) */}
            <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm">
                <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
                    <User size={20} className="text-blue-500"/>
                    {pageText.checkout.receiverSpecs}
                </h2>
                <p className="text-xs text-slate-400 mb-4">
                    {pageText.checkout.receiverHint}
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <input 
                        name="first_name" 
                        value={formData.first_name} 
                        onChange={handleInputChange} 
                        type="text" 
                        className="input input-bordered rounded-xl bg-slate-50" 
                        placeholder={pageText.checkout.firstName}
                    />
                    <input 
                        name="last_name" 
                        value={formData.last_name} 
                        onChange={handleInputChange} 
                        type="text" 
                        className="input input-bordered rounded-xl bg-slate-50" 
                        placeholder={pageText.checkout.lastName}
                    />
                    <div className="relative sm:col-span-2">
                        <input 
                            name="phone_number" 
                            value={formData.phone_number} 
                            onChange={handleInputChange} 
                            type="tel" 
                            className="input input-bordered rounded-xl bg-slate-50 w-full pl-10 dir-ltr text-right" 
                            placeholder={pageText.checkout.phone}
                        />
                        <Phone size={18} className="absolute left-3 top-3.5 text-slate-400" />
                    </div>
                </div>
            </div>

            {/* ۲. آدرس تحویل */}
            <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm">
                <h2 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
                    <MapPin size={20} className="text-orange-500"/>
                    {pageText.checkout.deliveryAddress}
                </h2>

                {/* تب‌بندی: انتخاب یا جدید */}
                {addresses.length > 0 && (
                    <div className="flex bg-slate-100 p-1 rounded-xl mb-6">
                        <button
                            onClick={() => setAddressMode('existing')}
                            className={clsx(
                                "flex-1 py-2 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2",
                                addressMode === 'existing' ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700"
                            )}
                        >
                            <Home size={16}/> {pageText.checkout.chooseFromList}
                        </button>
                        <button
                            onClick={() => setAddressMode('new')}
                            className={clsx(
                                "flex-1 py-2 rounded-lg text-sm font-bold transition-all flex items-center justify-center gap-2",
                                addressMode === 'new' ? "bg-white text-slate-800 shadow-sm" : "text-slate-500 hover:text-slate-700"
                            )}
                        >
                            <Plus size={16}/> {pageText.checkout.addNewAddress}
                        </button>
                    </div>
                )}

                {/* حالت الف: انتخاب از لیست */}
                {addressMode === 'existing' && (
                    <div className="grid grid-cols-1 gap-3">
                        {addresses.map((addr) => (
                            <div 
                                key={addr.id}
                                onClick={() => setSelectedAddressId(addr.id)}
                                className={clsx(
                                    "border-2 rounded-2xl p-4 cursor-pointer transition-all relative",
                                    selectedAddressId === addr.id 
                                        ? "border-blue-500 bg-blue-50/50" 
                                        : "border-slate-100 hover:border-slate-300"
                                )}
                            >
                                <div className="flex justify-between items-start">
                                    <p className="text-slate-700 font-medium text-sm leading-relaxed ml-6">
                                        {addr.province?.name || addr.province_name}، {addr.city?.name || addr.city_name}، {addr.address}
                                    </p>
                                    <div className={clsx(
                                        "w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0",
                                        selectedAddressId === addr.id ? "border-blue-600" : "border-slate-300"
                                    )}>
                                        {selectedAddressId === addr.id && <div className="w-2.5 h-2.5 rounded-full bg-blue-600" />}
                                    </div>
                                </div>
                                {addr.postal_code && (
                                    <span className="text-xs text-slate-400 mt-2 block font-mono">
                                        {pageText.checkout.postalCode} {addr.postal_code}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* حالت ب: ثبت آدرس جدید */}
                {addressMode === 'new' && (
                    <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                            <div className="form-control">
                                <label className="label"><span className="label-text">{pageText.checkout.province}</span></label>
                                <select 
                                    name="province_id" 
                                    value={formData.province_id} 
                                    onChange={handleProvinceChange}
                                    className="select select-bordered rounded-xl bg-slate-50"
                                >
                                    <option value="">{pageText.checkout.chooseProvince}</option>
                                    {provinces.map(p => (
                                        <option key={p.id} value={p.id}>{p.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-control">
                                <label className="label"><span className="label-text">{pageText.checkout.city}</span></label>
                                <select 
                                    name="city_id" 
                                    value={formData.city_id} 
                                    onChange={handleInputChange}
                                    className="select select-bordered rounded-xl bg-slate-50"
                                    disabled={!formData.province_id}
                                >
                                    <option value="">{pageText.checkout.chooseCity}</option>
                                    {cities.map(c => (
                                        <option key={c.id} value={c.id}>{c.name}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="form-control mb-4">
                            <label className="label"><span className="label-text">{pageText.checkout.addressDetails}</span></label>
                            <textarea 
                                name="address_text" 
                                value={formData.address_text} 
                                onChange={handleInputChange}
                                className="textarea textarea-bordered rounded-xl bg-slate-50 h-24" 
                                placeholder={pageText.checkout.addressPlaceholder}
                            ></textarea>
                        </div>

                        <div className="form-control sm:w-1/2">
                            <label className="label"><span className="label-text">{pageText.checkout.postalCodeLabel}</span></label>
                            <input 
                                name="postal_code" 
                                value={formData.postal_code} 
                                onChange={handleInputChange} 
                                type="text" 
                                className="input input-bordered rounded-xl bg-slate-50 dir-ltr text-right" 
                                placeholder={pageText.checkout.postalCodePlaceholder}
                            />
                        </div>
                    </div>
                )}
            </div>
          </div>

          {/* --- ستون چپ: فاکتور --- */}
          <div className="lg:col-span-4">
             <div className="sticky top-8 space-y-4">
                <div className="bg-white rounded-3xl p-6 shadow-xl shadow-slate-200/50 border border-slate-100">
                   <h3 className="font-bold text-slate-800 mb-4 border-b pb-3">{pageText.checkout.finalInvoice}</h3>
                   
                   <div className="space-y-3 mb-6 max-h-60 overflow-y-auto pr-1 custom-scrollbar">
                      {cartSummary.items.map(item => (
                          <div key={item.id} className="flex justify-between text-sm">
                              <span className="text-slate-600 truncate max-w-[60%]">
                                  {item.product?.name || item.name} 
                                  <span className="text-xs text-slate-400 mx-1">x{item.quantity}</span>
                              </span>
                              <span className="font-medium">{parseFloat(item.price).toLocaleString()}</span>
                          </div>
                      ))}
                   </div>

                   <div className="bg-slate-50 rounded-xl p-4 space-y-2 mb-6">
                       <div className="flex justify-between text-slate-600">
                           <span>{pageText.checkout.itemsTotal}</span>
                           <span className="font-bold">{cartSummary.total_price?.toLocaleString()}</span>
                       </div>
                       <div className="flex justify-between text-slate-400 text-sm">
                           <span>{pageText.checkout.shippingCost}</span>
                           <span>{pageText.checkout.postPaid}</span>
                       </div>
                       <div className="divider my-1"></div>
                       <div className="flex justify-between items-center">
                           <span className="text-lg font-bold text-slate-800">{pageText.checkout.payableAmount}</span>
                           <span className="text-2xl font-black text-blue-600">
                               {cartSummary.total_price?.toLocaleString()} <span className="text-xs font-normal">{pageText.checkout.currency}</span>
                           </span>
                       </div>
                   </div>

                   <button 
                     onClick={handleSubmit}
                     disabled={submitting}
                     className="w-full py-4 bg-emerald-600 text-white rounded-xl font-bold text-lg hover:bg-emerald-700 hover:shadow-lg hover:shadow-emerald-600/30 transition-all flex items-center justify-center gap-2"
                   >
                     {submitting ? (
                        <>
                            <span className="loading loading-spinner"></span>
                            {pageText.checkout.submitting}
                        </>
                     ) : (
                        <>
                            <CreditCard size={20} />
                            {pageText.checkout.confirmAndPay}
                        </>
                     )}
                   </button>
                </div>
             </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;