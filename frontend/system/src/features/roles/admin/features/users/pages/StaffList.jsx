import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { staffService } from "../api/staffService";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Plus, Users, RefreshCcw, ShieldAlert } from "lucide-react";
import { DataTable } from "@/components/ui/data-table"; // استفاده از جدول جنریک
import { getStaffColumns } from "../components/staffColumns";
import StaffForm from "../components/StaffForm";
import { toast } from "sonner";

const StaffList = () => {
  const queryClient = useQueryClient();
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState(null);

  // دریافت لیست پرسنل
  const { data: staffList = [], isLoading, refetch } = useQuery({
    queryKey: ["staff"],
    queryFn: staffService.getAllStaff,
  });

  const handleEdit = (staff) => {
    setEditingStaff(staff);
    setIsSheetOpen(true);
  };

  const handleCreate = () => {
    setEditingStaff(null);
    setIsSheetOpen(true);
  };

  // حذف تکی
  const deleteMutation = useMutation({
    mutationFn: staffService.deleteStaff,
    onSuccess: () => {
      toast.success("کارمند اخراج شد");
      queryClient.invalidateQueries({ queryKey: ["staff"] });
    }
  });

  const handleDelete = (id) => {
    if (confirm("آیا از حذف این کارمند اطمینان دارید؟ این عملیات غیرقابل بازگشت است.")) {
        deleteMutation.mutate(id);
    }
  };

  // ستون‌ها
  const columns = getStaffColumns(handleEdit, handleDelete);

  return (
    <div className="p-6 space-y-6 animate-in fade-in duration-500">
      
      {/* هدر صفحه */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 p-5 rounded-md border-b-4 border-gold-dark shadow-xl text-white">
        <div className="flex items-center gap-4">
          <div className="bg-slate-800 p-2.5 rounded-md border border-slate-700 text-gold-dark">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-black text-white tracking-tight">مدیریت پرسنل</h1>
            <p className="text-slate-400 text-xs mt-1">مدیریت حسابداران، طراحان و مدیران سیستم</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
             <Button variant="outline" size="sm" onClick={() => refetch()} className="border-slate-700 text-slate-300 hover:bg-white/10 h-10">
                <RefreshCcw className="h-4 w-4 ml-2" />
             </Button>
             <Button onClick={handleCreate} className="bg-gold-dark hover:bg-gold-dark/90 text-slate-900 font-bold h-10">
                <Plus className="h-4 w-4 ml-2" /> استخدام جدید
             </Button>
        </div>
      </div>

      {/* جدول */}
      <div className="bg-white rounded-md border border-slate-200 shadow-sm p-4">
         <DataTable 
            columns={columns} 
            data={staffList} 
            isLoading={isLoading} 
            searchKey="username" // ستونی که سرچ روی آن انجام میشود
         />
      </div>

      {/* Sheet فرم */}
      <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
        <SheetContent side="left" className="w-[400px] sm:w-[500px]">
          <SheetHeader className="text-right border-b pb-4 mb-4">
            <SheetTitle className="text-xl font-black text-slate-800 flex items-center gap-2">
                {editingStaff ? <ShieldAlert className="text-amber-500"/> : <Plus className="text-emerald-600"/>}
                {editingStaff ? "ویرایش اطلاعات کارمند" : "استخدام کارمند جدید"}
            </SheetTitle>
            <SheetDescription>
                {editingStaff 
                    ? "تغییر نقش سازمانی یا وضعیت فعالیت." 
                    : "تعریف حساب کاربری جدید برای پرسنل شرکت."}
            </SheetDescription>
          </SheetHeader>
          
          <StaffForm 
            staffToEdit={editingStaff} 
            onSuccess={() => setIsSheetOpen(false)} 
          />
        </SheetContent>
      </Sheet>

    </div>
  );
};

export default StaffList;