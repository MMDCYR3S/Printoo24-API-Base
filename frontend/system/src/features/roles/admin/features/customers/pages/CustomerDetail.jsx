import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { customerService } from "../api/customerService";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  ArrowRight, User, Phone, Mail, Building2, MapPin, 
  Trash2, Edit, Plus, UserX, UserCheck, AlertCircle 
} from "lucide-react";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { toast } from "sonner";
import CustomerForm from "../components/CustomerForm";
import AddressDialog from "../components/AddressDialog";

const CustomerDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  // استیت‌های مودال‌ها
  const [isEditSheetOpen, setIsEditSheetOpen] = useState(false);
  const [isAddressDialogOpen, setIsAddressDialogOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null); // آدرسی که داره ادیت میشه

  // 1. دریافت اطلاعات مشتری
  const { data: customer, isLoading, isError } = useQuery({
    queryKey: ["customer", id],
    queryFn: () => customerService.getCustomerById(id),
  });

  // 2. حذف مشتری
  const deleteCustomerMutation = useMutation({
    mutationFn: customerService.deleteCustomer,
    onSuccess: () => {
      toast.success("مشتری با موفقیت حذف شد");
      navigate("/admin/customers");
    }
  });

  // 3. افزودن/ویرایش آدرس
  const addressMutation = useMutation({
    mutationFn: (data) => {
        if (editingAddress) {
            return customerService.updateAddress({ userId: id, addressId: editingAddress.id, addressData: data });
        } else {
            return customerService.createAddress({ userId: id, addressData: data });
        }
    },
    onSuccess: () => {
        toast.success(editingAddress ? "آدرس ویرایش شد" : "آدرس جدید اضافه شد");
        queryClient.invalidateQueries({ queryKey: ["customer", id] }); // رفرش صفحه
        setIsAddressDialogOpen(false);
    },
    onError: () => toast.error("خطا در ذخیره آدرس")
  });

  // 4. حذف آدرس
  const deleteAddressMutation = useMutation({
      mutationFn: (addressId) => customerService.deleteAddress({ userId: id, addressId }),
      onSuccess: () => {
          toast.success("آدرس حذف شد");
          queryClient.invalidateQueries({ queryKey: ["customer", id] });
      }
  });

  if (isLoading) return <div className="p-10 text-center">در حال بارگذاری اطلاعات مشتری...</div>;
  if (isError) return <div className="p-10 text-center text-red-500">خطا در دریافت اطلاعات.</div>;

  return (
    <div className="max-w-[1600px] mx-auto p-6 space-y-6 pb-20 animate-in fade-in duration-500">
      
      {/* --- هدر صفحه --- */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-4">
            <Button variant="outline" size="icon" onClick={() => navigate(-1)}>
                <ArrowRight className="h-4 w-4" />
            </Button>
            <div className="flex items-center gap-4">
                <div className="h-14 w-14 bg-slate-100 rounded-full flex items-center justify-center text-xl font-black text-slate-500 border-2 border-slate-200">
                    {customer.first_name?.[0]}{customer.last_name?.[0]}
                </div>
                <div>
                    <h1 className="text-2xl font-black text-slate-800 flex items-center gap-2">
                        {customer.first_name} {customer.last_name}
                        {customer.is_active ? 
                            <Badge className="bg-emerald-100 text-emerald-700 hover:bg-emerald-200 border-0 text-[10px] h-5"><UserCheck className="w-3 h-3 ml-1"/> فعال</Badge> : 
                            <Badge className="bg-rose-100 text-rose-700 hover:bg-rose-200 border-0 text-[10px] h-5"><UserX className="w-3 h-3 ml-1"/> غیرفعال</Badge>
                        }
                    </h1>
                    <span className="text-slate-400 text-sm font-mono">@{customer.username}</span>
                </div>
            </div>
        </div>

        <div className="flex items-center gap-2">
            <Button variant="outline" className="border-slate-300 text-slate-700" onClick={() => setIsEditSheetOpen(true)}>
                <Edit className="ml-2 h-4 w-4" /> ویرایش پروفایل
            </Button>
            <Button 
                variant="destructive" 
                onClick={() => {
                    if(confirm("آیا از حذف کل حساب کاربری این مشتری اطمینان دارید؟")) 
                        deleteCustomerMutation.mutate(id);
                }}
            >
                <Trash2 className="ml-2 h-4 w-4" /> حذف حساب
            </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          
          {/* --- ستون راست: اطلاعات هویتی --- */}
          <div className="xl:col-span-1 space-y-6">
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                  <div className="bg-slate-50 p-4 border-b font-bold text-slate-700 flex items-center gap-2">
                      <User className="h-4 w-4" /> اطلاعات تماس
                  </div>
                  <div className="p-5 space-y-4">
                      <div className="flex items-center gap-3 text-sm">
                          <Phone className="h-4 w-4 text-slate-400" />
                          <span className="font-mono dir-ltr text-slate-700 font-bold">{customer.phone_number}</span>
                      </div>
                      {customer.email && (
                        <div className="flex items-center gap-3 text-sm">
                            <Mail className="h-4 w-4 text-slate-400" />
                            <span className="font-mono dir-ltr text-slate-700">{customer.email}</span>
                        </div>
                      )}
                      {customer.company && (
                        <div className="flex items-center gap-3 text-sm">
                            <Building2 className="h-4 w-4 text-slate-400" />
                            <span className="text-slate-700">{customer.company}</span>
                        </div>
                      )}
                  </div>
              </div>
          </div>

          {/* --- ستون چپ: مدیریت آدرس‌ها --- */}
          <div className="xl:col-span-2 space-y-6">
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm min-h-[300px]">
                  <div className="bg-slate-50 p-4 border-b flex justify-between items-center">
                      <div className="font-bold text-slate-700 flex items-center gap-2">
                          <MapPin className="h-4 w-4" /> دفترچه آدرس‌ها
                      </div>
                      <Button size="sm" className="bg-gold-dark text-slate-900 hover:bg-gold-dark/90 h-8 text-xs" onClick={() => {
                          setEditingAddress(null);
                          setIsAddressDialogOpen(true);
                      }}>
                          <Plus className="ml-1 h-3.5 w-3.5" /> آدرس جدید
                      </Button>
                  </div>
                  
                  <div className="p-5 grid grid-cols-1 md:grid-cols-2 gap-4">
                      {customer.addresses && customer.addresses.length > 0 ? (
                          customer.addresses.map((addr) => (
                              <div key={addr.id} className="border border-slate-200 rounded-lg p-4 hover:border-blue-300 transition-colors group relative bg-slate-50/50">
                                  <div className="flex items-start gap-3">
                                      <div className="bg-white p-2 rounded-full border border-slate-100 shadow-sm text-slate-400">
                                          <MapPin className="h-5 w-5" />
                                      </div>
                                      <div className="flex-1">
                                          <div className="text-xs text-slate-400 font-bold mb-1">
                                              {addr.province} - {addr.city}
                                          </div>
                                          <p className="text-sm text-slate-700 leading-relaxed font-medium">
                                              {addr.address}
                                          </p>
                                          {addr.postal_code && (
                                              <div className="mt-2 text-xs font-mono bg-white inline-block px-2 py-0.5 rounded border border-slate-100 text-slate-500">
                                                  {addr.postal_code}
                                              </div>
                                          )}
                                      </div>
                                  </div>
                                  
                                  {/* دکمه‌های عملیات روی آدرس */}
                                  <div className="absolute top-3 left-3 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                      <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-400 hover:text-blue-600 hover:bg-blue-50" 
                                          onClick={() => {
                                              setEditingAddress(addr);
                                              setIsAddressDialogOpen(true);
                                          }}>
                                          <Edit className="h-3.5 w-3.5" />
                                      </Button>
                                      <Button variant="ghost" size="icon" className="h-7 w-7 text-slate-400 hover:text-red-600 hover:bg-red-50"
                                          onClick={() => {
                                              if(confirm("آیا این آدرس حذف شود؟")) deleteAddressMutation.mutate(addr.id);
                                          }}>
                                          <Trash2 className="h-3.5 w-3.5" />
                                      </Button>
                                  </div>
                              </div>
                          ))
                      ) : (
                          <div className="col-span-full py-10 flex flex-col items-center justify-center text-slate-400 border-2 border-dashed border-slate-100 rounded-lg">
                              <AlertCircle className="h-8 w-8 mb-2 opacity-50" />
                              <p>هیچ آدرسی ثبت نشده است.</p>
                          </div>
                      )}
                  </div>
              </div>
          </div>
      </div>

      {/* --- Sheet ویرایش اطلاعات هویتی --- */}
      <Sheet open={isEditSheetOpen} onOpenChange={setIsEditSheetOpen}>
        <SheetContent side="left" className="w-[400px] sm:w-[540px]">
           <SheetHeader>
               <SheetTitle>ویرایش اطلاعات مشتری</SheetTitle>
           </SheetHeader>
           {/* استفاده مجدد از فرمی که قبلا ساختیم */}
           <CustomerForm 
               customerToEdit={customer} 
               onSuccess={() => {
                   setIsEditSheetOpen(false);
                   queryClient.invalidateQueries({ queryKey: ["customer", id] });
               }} 
            />
        </SheetContent>
      </Sheet>

      {/* --- Dialog مدیریت آدرس --- */}
      <AddressDialog 
          open={isAddressDialogOpen}
          onOpenChange={setIsAddressDialogOpen}
          initialData={editingAddress}
          onSubmit={(data) => addressMutation.mutate(data)}
          isSubmitting={addressMutation.isPending}
      />

    </div>
  );
};

export default CustomerDetail;