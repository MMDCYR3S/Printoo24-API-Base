import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { designService } from "../services/designService";
import { toast } from "sonner";

export const useDesignOrders = (id = null) => {
  const queryClient = useQueryClient();

  const ordersQuery = useQuery({
    queryKey: ["design-orders"],
    queryFn: designService.getOrders
  });

  const detailQuery = useQuery({
    queryKey: ["design-order", id],
    queryFn: () => designService.getOrderDetail(id),
    enabled: !!id
  });

  const approveMutation = useMutation({
    mutationFn: designService.approveOrder,
    onSuccess: () => {
      toast.success("سفارش تایید و به مرحله بعد منتقل شد");
      queryClient.invalidateQueries(["design-orders"]);
    }
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, description }) => designService.rejectOrder(id, description),
    onSuccess: () => {
      toast.error("سفارش رد شد");
      queryClient.invalidateQueries(["design-orders"]);
    }
  });

  return {
    orders: ordersQuery.data || [],
    isLoading: ordersQuery.isLoading,
    orderDetail: detailQuery.data,
    isDetailLoading: detailQuery.isLoading,
    approve: approveMutation.mutate,
    reject: rejectMutation.mutate,
    isActionLoading: approveMutation.isPending || rejectMutation.isPending
  };
};