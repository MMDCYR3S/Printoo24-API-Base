from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.models import Expense, Invoice
from core.financial.services import ExpenseService
from api.v1.dashboard.serializers import (
    ExpenseSerializer,
    ExpenseCreateSerializer,
    ExpenseUpdateSerializer,
    ExpenseStatsSerializer,
    UnlockedInvoiceOrderSerializer
)


class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Expense.objects.get_expenses_with_order()
    service = ExpenseService()  # نمونه سرویس

    def get_serializer_class(self):
        if self.action == 'create':
            return ExpenseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ExpenseUpdateSerializer
        return ExpenseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expense = self.service.create_expense(
            name=serializer.validated_data['name'],
            amount=serializer.validated_data['amount'],
            order=serializer.validated_data.get('order'),
            expense_type=serializer.validated_data.get('expense_type', 'other'),
            quantity=serializer.validated_data.get('quantity', 1),
            unit_price=serializer.validated_data.get('unit_price'),
            description=serializer.validated_data.get('description', ''),
            receipt=serializer.validated_data.get('receipt'),
            registered_by=request.user,
        )
        return Response(ExpenseSerializer(expense).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        expense = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_expense(
            expense_id=expense.id,
            data=serializer.validated_data,
            actor=request.user,
        )
        return Response(ExpenseSerializer(updated).data)

    def partial_update(self, request, *args, **kwargs):
        expense = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = self.service.update_expense(
            expense_id=expense.id,
            data=serializer.validated_data,
            actor=request.user,
        )
        return Response(ExpenseSerializer(updated).data)

    def destroy(self, request, *args, **kwargs):
        expense = self.get_object()
        self.service.delete_expense(expense.id, actor=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='statistics')
    def get_statistics(self, request):
        # آمار هزینه‌ها و سود از منیجرهای اصلاح‌شده
        stats = {
            'total_expenses': Expense.objects.get_total_expenses(),
            'daily_expenses': Expense.objects.get_daily_expenses(),
            'monthly_expenses': Expense.objects.get_monthly_expenses(),
            'yearly_expenses': Expense.objects.get_yearly_expenses(),
            'daily_profit': Invoice.objects.get_daily_profit(),
            'monthly_profit': Invoice.objects.get_monthly_profit(),
            'yearly_profit': Invoice.objects.get_yearly_profit(),
        }
        return Response(ExpenseStatsSerializer(instance=stats).data)

    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>[0-9]+)')
    def get_order_expenses(self, request, order_id=None):
        expenses = self.service.get_order_expenses(int(order_id))
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='unlocked-invoices')
    def list_unlocked_invoice_orders(self, request):
        orders = self.service.get_orders_with_unlocked_invoices()
        serializer = UnlockedInvoiceOrderSerializer(orders, many=True)
        return Response(serializer.data)