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

# ========== EXPENSE VIEWSET ========== #
class ExpenseViewSet(viewsets.ModelViewSet):
    """
    مدیریت CRUD هزینه‌ها.
    
    - لیست هزینه‌ها
    - ایجاد هزینه جدید
    - ویرایش هزینه
    - حذف هزینه
    - دریافت آمار هزینه‌ها و سود
    """
    
    permission_classes = [IsAdminUser]
    queryset = Expense.objects.get_expenses_with_order()
    
    def get_serializer_class(self):
        """انتخاب سریالایزر براساس اکشن"""
        if self.action == 'create':
            return ExpenseCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ExpenseUpdateSerializer
        return ExpenseSerializer
    
    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="لیست تمام هزینه‌ها",
        description="دریافت لیست کامل هزینه‌ها همراه با اطلاعات سفارش مرتبط"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="ایجاد هزینه جدید",
        request=ExpenseCreateSerializer,
        responses={201: ExpenseSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        expense = ExpenseService.create_expense(
            name=serializer.validated_data['name'],
            amount=serializer.validated_data['amount'],
            order=serializer.validated_data.get('order')
        )

        output_serializer = ExpenseSerializer(expense)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="جزئیات یک هزینه",
        responses={200: ExpenseSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="بروزرسانی کامل هزینه",
        request=ExpenseUpdateSerializer,
        responses={200: ExpenseSerializer}
    )
    def update(self, request, *args, **kwargs):
        expense = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_expense = ExpenseService.update_expense(
            expense_id=expense.id,
            data=serializer.validated_data
        )
        
        output_serializer = ExpenseSerializer(updated_expense)
        return Response(output_serializer.data)
    
    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="بروزرسانی جزئی هزینه",
        request=ExpenseUpdateSerializer,
        responses={200: ExpenseSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        expense = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_expense = ExpenseService.update_expense(
            expense_id=expense.id,
            data=serializer.validated_data
        )
        
        output_serializer = ExpenseSerializer(updated_expense)
        return Response(output_serializer.data)
    
    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="حذف هزینه",
        responses={204: None}
    )
    def destroy(self, request, *args, **kwargs):
        expense = self.get_object()
        ExpenseService.delete_expense(expense.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="دریافت آمار کلی هزینه‌ها و سود",
        responses={200: ExpenseStatsSerializer}
    )
    @action(detail=False, methods=['get'], url_path='statistics')
    def get_statistics(self, request):
        """
        آمار کامل هزینه‌ها و سود روزانه/ماهانه/سالانه.
        """
        stats = {
            'total_expenses': Expense.objects.get_total_expenses(),
            'daily_expenses': Expense.objects.get_daily_expenses(),
            'monthly_expenses': Expense.objects.get_monthly_expenses(),
            'yearly_expenses': Expense.objects.get_yearly_expenses(),
            
            'daily_profit': Invoice.objects.get_daily_profit(),
            'monthly_profit': Invoice.objects.get_monthly_profit(),
            'yearly_profit': Invoice.objects.get_yearly_profit(),
        }
        
        serializer = ExpenseStatsSerializer(instance=stats)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="هزینه‌های یک سفارش خاص",
        parameters=[
            OpenApiParameter(name='order_id', type=int, location=OpenApiParameter.PATH)
        ],
        responses={200: ExpenseSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>[0-9]+)')
    def get_order_expenses(self, request, order_id=None):
        """
        دریافت تمام هزینه‌های مرتبط با یک سفارش.
        """
        expenses = Expense.objects.get_order_expenses(order_id)
        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Dashboard - Expenses'],
        summary="لیست سفارشات دارای فاکتور قفل‌نشده",
        description="دریافت تمامی سفارشاتی که فاکتور برای آن‌ها صادر شده اما هنوز نهایی/قفل نشده‌اند.",
        responses={200: UnlockedInvoiceOrderSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='unlocked-invoices')
    def list_unlocked_invoice_orders(self, request):
        """
        بازگرداندن لیست کامل سفارشات با فاکتورهای باز (قفل‌نشده)
        """
        orders = ExpenseService.get_orders_with_unlocked_invoices()

        serializer = UnlockedInvoiceOrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
