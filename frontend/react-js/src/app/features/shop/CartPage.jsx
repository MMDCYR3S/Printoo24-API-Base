import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingBag, CreditCard, ShieldCheck, AlertCircle } from 'lucide-react';
import { cartService } from '../../services/cartService';
import CartItem from './components/CartItem';
import { toast } from 'react-hot-toast';

import pageText from '../../lang/pages.json';
import globalText from '../../lang/global.json';

const CartPage = () => {
  const [cartData, setCartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const navigate = useNavigate();

  const fetchCart = async () => {
    try {
      setLoading(true);
      const data = await cartService.getCartItems();
      setCartData(data);
    } catch (err) {
      console.error(err);
      toast.error(pageText.cart.cartPage.fetchCartError);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleDeleteItem = async (itemId) => {
    if (!window.confirm(pageText.cart.cartPage.deleteConfirm)) return;
    setDeletingId(itemId);
    try {
      await cartService.deleteItem(itemId);
      toast.success(pageText.cart.cartPage.deleteSuccess);
      fetchCart();
    } catch (err) {
      toast.error(pageText.cart.cartPage.deleteError);
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <span className="loading loading-spinner loading-lg text-primary"></span>
      </div>
    );
  }

  if (!cartData || !cartData.items || cartData.items.length === 0) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4">
        <div className="w-24 h-24 bg-slate-200 rounded-full flex items-center justify-center text-slate-400 mb-6">
          <ShoppingBag size={48} />
        </div>
        <h1 className="text-2xl font-bold text-slate-800 mb-2">{pageText.cart.cartPage.emptyCartTitle}</h1>
        <Link to="/shop" className="btn btn-primary px-8 rounded-xl mt-4">{pageText.cart.cartPage.viewProducts}</Link>
      </div>
    );
  }

  // چک میکنیم کدوم آیتم ها فایل ندارن (فقط برای نمایش وارنینگ، نه بستن دکمه)
  const itemsWithoutFiles = cartData.items.filter(item => !item.uploads || item.uploads.length === 0);

  return (
    <div className="bg-slate-50 min-h-screen pb-20 pt-8">
      <div className="container mx-auto px-4 max-w-7xl">
        
        <div className="flex items-center gap-3 mb-8">
          <h1 className="text-3xl font-black text-slate-800">{pageText.cart.cartPage.pageTitle}</h1>
          <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-bold">
            {pageText.cart.cartPage.productUnit.replace('{{count}}', cartData.items.length)}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-8">
            {cartData.items.map((item) => (
              <CartItem 
                key={item.id} 
                item={item} 
                onDelete={handleDeleteItem}
                isDeleting={deletingId === item.id}
              />
            ))}
          </div>

          <div className="lg:col-span-4">
             <div className="sticky top-8 space-y-4">
                <div className="bg-white rounded-3xl p-6 shadow-xl shadow-slate-200/50 border border-slate-100">
                   <h2 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                     <CreditCard size={20} className="text-blue-600"/>
                     {pageText.cart.cartPage.summaryTitle}
                   </h2>

                   <div className="space-y-3 text-sm text-slate-600 mb-6">
                      <div className="flex justify-between">
                        <span>{pageText.cart.cartPage.itemCountLabel}</span>
                        <span className="font-bold">{cartData.items.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>{pageText.cart.cartPage.subtotalLabel}</span>
                        <span className="font-bold text-slate-800">{cartData.total_price?.toLocaleString()} {pageText.cart.cartPage.currency}</span>
                      </div>
                   </div>

                   <div className="border-t border-slate-100 py-4 mb-4">
                     <div className="flex justify-between items-center">
                        <span className="font-bold text-slate-800">{pageText.cart.cartPage.totalPayableLabel}</span>
                        <div className="text-right">
                            <span className="block text-2xl font-black text-blue-600">
                              {cartData.total_price?.toLocaleString()}
                            </span>
                            <span className="text-xs text-slate-400">{pageText.cart.cartPage.currency}</span>
                        </div>
                     </div>
                   </div>

                   {/* نمایش پیام اطلاع رسانی بجای خطا */}
                   {itemsWithoutFiles.length > 0 && (
                     <div className="bg-blue-50 text-blue-800 text-xs p-3 rounded-xl mb-4 flex items-start gap-2">
                       <AlertCircle size={16} className="shrink-0 mt-0.5" />
                       <p>{pageText.cart.cartPage.noFileWarning.replace('{{count}}', itemsWithoutFiles.length)}</p>
                     </div>
                   )}

                   {/* دکمه همیشه فعال است */}
                   <button 
                     onClick={() => navigate('/checkout')} // هنوز صفحه چک‌اوت نداریم ولی آماده‌اش میکنیم
                     className="w-full py-4 bg-primary text-white rounded-xl font-bold text-lg hover:shadow-lg hover:shadow-primary/30 transition-all"
                   >
                     {pageText.cart.cartPage.checkoutBtn}
                   </button>
                </div>


             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;