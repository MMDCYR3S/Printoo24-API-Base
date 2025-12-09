import django_filters
from django.db.models import Q
from core.models import Order

class OrderFilter(django_filters.FilterSet):
    """
    فیلریتنگ مربوط به لیست سفارشات و نمایش آن در داشبورد اختصاصی هر کاربر
    """
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    search = django_filters.CharFilter(method='custom_search', label="Search")
    
    status = django_filters.CharFilter(field_name='current_status__internal_code')

    class Meta:
        model = Order
        fields = ['type', 'order_code']

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(order_code__icontains=value) |
            Q(user__username__icontains=value) |
            Q(user__email__icontains=value) |
            Q(user__customer_profile__last_name__icontains=value) |
            Q(invoice_order__invoice_number__icontains=value)
        )