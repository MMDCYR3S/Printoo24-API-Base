import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { customerService } from "../api/customerService";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Plus, Users, Search, RefreshCcw } from "lucide-react";
import { Input } from "@/components/ui/input";
import OrdersDataTable from "@/features/shared/orders/components/OrdersDataTable"; // استفاده مجدد از جدولی که ساختیم!
import { getCustomerColumns } from "../components/customerColumns";
import CustomerForm from "../components/CustomerForm";
import { toast } from "sonner";
import { DataTable } from "@/components/ui/data-table";

const CustomerList = () => {
  const queryClient = useQueryClient();
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);

  // دریافت لیست مشتریان
  const { data: customers = [], isLoading, isError, refetch } = useQuery({
    queryKey: ["customers"],
    // queryFn: customerService.getAllCustomers,
    queryFn: () => customerService.searchCustomers(),
  });

  // هندل کردن باز شدن فرم برای ادیت
  const handleEdit = (customer) => {
    setEditingCustomer(customer);
    setIsSheetOpen(true);
  };

  // هندل کردن باز شدن فرم برای جدید
  const handleCreate = () => {
    setEditingCustomer(null);
    setIsSheetOpen(true);
  };

  // هندل کردن حذف تکی
  const deleteMutation = useMutation({
    mutationFn: customerService.deleteCustomer,
    onSuccess: () => {
      toast.success("مشتری حذف شد");
      queryClient.invalidateQueries({ queryKey: ["customers"] });
    }
  });

  const handleDelete = (id) => {
    if (confirm("آیا از حذف این مشتری اطمینان دارید؟")) {
        deleteMutation.mutate(id);
    }
  };

  // هندل کردن حذف گروهی (پاس داده میشه به جدول)
  const bulkDeleteMutation = useMutation({
      mutationFn: (ids) => customerService.bulkAction({ action: 'delete', ids }),
      onSuccess: () => {
        toast.success("مشتریان انتخاب شده حذف شدند");
        queryClient.invalidateQueries({ queryKey: ["customers"] });
      }
  });

  // ستون‌ها
  const columns = getCustomerColumns(handleEdit, handleDelete);

  return (
    <div className="p-6 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* هدر صفحه */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 p-5 rounded-md border-b-4 border-gold-dark shadow-xl text-white">
        <div className="flex items-center gap-4">
          <div className="bg-gold-dark p-2.5 rounded-md shadow-inner text-slate-900">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-black text-gold-light tracking-tight">مدیریت مشتریان</h1>
            <p className="text-slate-400 text-xs mt-1">مشاهده و مدیریت کاربران حقیقی و حقوقی</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
             <Button variant="outline" size="sm" onClick={() => refetch()} className="border-slate-700 text-slate-300 hover:bg-white/10 h-10">
                <RefreshCcw className="h-4 w-4 ml-2" /> بروزرسانی
             </Button>
             <Button onClick={handleCreate} className="bg-gold-dark hover:bg-gold-dark/90 text-slate-900 font-bold h-10">
                <Plus className="h-4 w-4 ml-2" /> مشتری جدید
             </Button>
        </div>
      </div>

      {/* جدول (از همون کامپوننت قدرتمندی که برای سفارشات ساختیم استفاده میکنیم) */}
      {/* نکته: ممکنه لازم باشه OrdersDataTable رو کمی جنرال تر کنی یا کپی کنی اسمشو بذاری DataTable */}
      {/* فعلا فرض میکنیم OrdersDataTable رو انقدر قوی نوشتیم که هر دیتایی بگیره */}
      
      {/* البته چون ستون های مشتری متفاوته، باید مطمئن بشیم OrdersDataTable فقط ستون های خودش رو نمیخونه */}
      {/* راهکار سریع: یک کپی از OrdersDataTable بساز به نام CustomersDataTable یا همون رو جنریک کن */}
      {/* من اینجا فرض میکنم یک کپی ساختی به نام CustomersDataTable که دقیقا همونه فقط columns رو از props میگیره */}
      
{/* جدول مشتریان */}
<div className="bg-white rounded-md border border-slate-200 shadow-sm p-4">
   <DataTable 
      columns={columns} 
      data={customers} 
      isLoading={isLoading} 
   />
</div>


      {/* پنل کشویی (Sheet) برای افزودن/ویرایش */}
      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent side="left" className="w-[400px] sm:w-[540px] overflow-y-auto">
          <SheetHeader className="text-right">
            <SheetTitle className="text-xl font-black text-slate-800 border-b pb-4 mb-4">
                {editingCustomer ? "ویرایش پرونده مشتری" : "ثبت نام مشتری جدید"}
            </SheetTitle>
            <SheetDescription>
                {editingCustomer 
                    ? "اطلاعات مشتری را تغییر دهید و ذخیره کنید." 
                    : "اطلاعات مشتری جدید را وارد کنید. نام کاربری و رمز عبور الزامی است."}
            </SheetDescription>
          </SheetHeader>
          
          <CustomerForm 
            customerToEdit={editingCustomer} 
            onSuccess={() => setIsSheetOpen(false)} 
          />
        </SheetContent>
      </Sheet>

    </div>
  );
};

export default CustomerList;