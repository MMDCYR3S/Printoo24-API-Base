from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.core.exceptions import ValidationError, PermissionDenied
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiTypes

from apps.accounts.services import CustomerAppService 
from ..serializers import (
    CustomerListSerializer, CustomerCreateSerializer, CustomerUpdateSerializer,
    BulkIdsSerializer, AddressSerializer, ProvinceSerializer, CitySerializer,
    CustomerDetailSerializer,
)

# ========== CUSTOMER MANAGEMENT VIEWS ========== #
@extend_schema(tags=["Users-Customers"])
class CustomerListCreateView(GenericAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerAppService()

    @extend_schema(
        summary="لیست تمام مشتریان",
        description="لیست کاربرانی که نقش مشتری (Customer) دارند به همراه اطلاعات پروفایل.",
        responses={200: CustomerListSerializer(many=True)}
    )
    def get(self, request):
        """ لیست تمام مشتریان """
        try:
            customers = self.service.get_customer_list(request.user)
            serializer = CustomerListSerializer(customers, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="ثبت نام مشتری جدید (توسط ادمین)",
        description="""
        ایجاد یک مشتری جدید به همراه پروفایل.
        
        **نکات:**
        * به صورت خودکار نقش `normal` (مشتری) به او داده می‌شود.
        * پروفایل `CustomerProfile` همزمان ایجاد می‌شود.
        """,
        request=CustomerCreateSerializer,
        responses={
            201: CustomerListSerializer,
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                'New Customer Example',
                value={
                    "username": "customer_1",
                    "email": "cust@example.com",
                    "password": "Password123!",
                    "first_name": "Ali",
                    "last_name": "Rezaei",
                    "phone_number": "09120000000",
                    "company": "Tech Corp"
                },
                request_only=True
            )
        ]
    )
    def post(self, request):
        """ ایجاد مشتری جدید """
        serializer = CustomerCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = self.service.create_customer(request.user, serializer.validated_data)
                return Response(CustomerListSerializer(user).data, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ========== CUSTOMER DETAIL VIEW ========== #
@extend_schema(tags=["Users-Customers"])
class CustomerDetailView(GenericAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerAppService()

    @extend_schema(
        summary="مشاهده جزئیات کامل مشتری",
        description="دریافت اطلاعات هویتی، پروفایل و لیست تمام آدرس‌های یک مشتری.",
        responses={200: CustomerDetailSerializer}
    )
    def get(self, request, pk):
        """ دریافت جزئیات مشتری """
        try:
            customer = self.service.get_customer_details(request.user, pk)
            if not customer:
                return Response({"detail": "مشتری یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
                
            serializer = CustomerDetailSerializer(customer)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="ویرایش اطلاعات مشتری",
        description="امکان ویرایش اطلاعات کاربری و پروفایل به صورت همزمان.",
        request=CustomerUpdateSerializer,
        responses={200: CustomerListSerializer}
    )
    def put(self, request, pk):
        """ ویرایش مشتری """
        serializer = CustomerUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = self.service.update_customer(request.user, pk, serializer.validated_data)
                return Response(CustomerListSerializer(user).data)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="حذف مشتری")
    def delete(self, request, pk):
        """ حذف مشتری """
        try:
            self.service.delete_customer(request.user, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ========== BULK ACTION VIEWS ========== #
@extend_schema(tags=["Users-Customers"])
class CustomerBulkActionsView(GenericAPIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerAppService()

    @extend_schema(
        summary="عملیات گروهی روی مشتریان",
        parameters=[
            OpenApiParameter(
                name='action',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description='نوع عملیات: delete, activate, deactivate',
                enum=['delete', 'activate', 'deactivate']
            )
        ],
        request=BulkIdsSerializer, 
        responses={200: OpenApiTypes.OBJECT}
    )
    def post(self, request, action):
        """
        مدیریت عملیات گروهی.
        """
        serializer = BulkIdsSerializer(data=request.data)
        if serializer.is_valid():
            try:
                ids = serializer.validated_data['ids']
                
                if action == 'delete':
                    result = self.service.bulk_delete(request.user, ids)
                    return Response(result)

                elif action == 'activate':
                    count = self.service.bulk_toggle_active(request.user, ids, True)
                    return Response({"updated_count": count})

                elif action == 'deactivate':
                    count = self.service.bulk_toggle_active(request.user, ids, False)
                    return Response({"updated_count": count})
                
                else:
                    return Response({"detail": "اکشن نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== CUSTOMER ADDRESS VIEWS ========== #
@extend_schema(tags=["Users-Customers-Address"])
class CustomerAddressManagementView(GenericAPIView):
    """
    مدیریت آدرس‌های یک مشتری خاص.
    URL: /customers/<int:user_id>/addresses/
    """
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = AddressSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerAppService()

    def get(self, request, user_id):
        """ لیست آدرس‌های مشتری """
        addresses = self.service.get_customer_addresses(request.user, user_id)
        serializer = self.get_serializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        """ افزودن آدرس جدید به مشتری """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                addr = self.service.add_address_to_customer(request.user, user_id, serializer.validated_data)
                return Response(self.get_serializer(addr).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== CUSTOMER ADDRESS VIEW ========== #
@extend_schema(tags=["Users-Customers-Address"])
class CustomerAddressDetailView(GenericAPIView):
    """
    ویرایش و حذف یک آدرس خاص.
    URL: /customers/<int:user_id>/addresses/<int:address_id>/
    """
    permission_classes = [IsAdminUser, IsAuthenticated]
    serializer_class = AddressSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerAppService()

    def put(self, request, user_id, address_id):
        """ ویرایش آدرس """
        serializer = self.get_serializer(data=request.data, partial=True)
        if serializer.is_valid():
            updated_addr = self.service.update_customer_address(
                request.user, user_id, address_id, serializer.validated_data
            )
            if updated_addr:
                return Response(self.get_serializer(updated_addr).data)
            return Response({"detail": "آدرس یافت نشد."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id, address_id):
        """ حذف آدرس """
        success = self.service.delete_customer_address(request.user, user_id, address_id)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "آدرس یافت نشد."}, status=status.HTTP_404_NOT_FOUND)


# ========== GEO LOCATION VIEWS (Utils) ========== #
@extend_schema(tags=["Utils-Geo"])
class ProvinceListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProvinceSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerAppService()

    def get(self, request):
        provinces = self.service.get_provinces()
        return Response(ProvinceSerializer(provinces, many=True).data)

@extend_schema(tags=["Utils-Geo"])
class CityListView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CitySerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CustomerAppService()

    @extend_schema(
        parameters=[
            OpenApiParameter(name='province_id', description='فیلتر بر اساس شناسه استان', required=False, type=int)
        ]
    )
    def get(self, request):
        province_id = request.query_params.get('province_id')
        cities = self.service.get_cities(province_id)
        return Response(CitySerializer(cities, many=True).data)
