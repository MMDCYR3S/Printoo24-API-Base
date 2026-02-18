import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Check, X, Loader2 } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

export default function DesignActions({ orderId, onApprove, onReject, isLoading }) {
  const [reason, setReason] = useState("");
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  return (
    <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
      <Button 
        size="sm" 
        className="bg-green-600 hover:bg-green-700 text-white gap-1"
        onClick={() => onApprove(orderId)}
        disabled={isLoading}
      >
        {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
        تایید طراحی
      </Button>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogTrigger asChild>
          <Button size="sm" variant="destructive" className="gap-1">
            <X className="h-4 w-4" />
            رد فایل
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>علت رد سفارش چیست؟</DialogTitle>
          </DialogHeader>
          <Textarea 
            placeholder="مثلاً: کیفیت فایل ارسالی پایین است..." 
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <DialogFooter>
            <Button 
              variant="destructive" 
              onClick={() => {
                onReject({ orderId, description: reason });
                setIsDialogOpen(false);
              }}
              disabled={!reason || isLoading}
            >
              ثبت رد و بازگشت
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}