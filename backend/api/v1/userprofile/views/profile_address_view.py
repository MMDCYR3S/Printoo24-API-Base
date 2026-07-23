from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter

from apps.userprofile.services import UserAddressService
from ..serializers import AddressSerializer, ProvinceSerializer, CitySerializer

# ===== User Address List Create APIView ===== #
@extend_schema(tags=["Profile"])
class UserAddressListCreateAPIView(GenericAPIView):
    """
    لیست آدرس های کاربر
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserAddressService()

    @extend_schema(
        summary="لیست آدرس‌های کاربر",
        responses={200: AddressSerializer(many=True)},
        examples=[
            OpenApiExample(
                'Address List Example',
                summary='لیست آدرس‌ها (GET)',
                description='خروجی شامل جزئیات کامل استان و شهر است.',
                value=[
                    {
                        "id": 1,
                        "province_detail": {"id": 8, "name": "تهران", "slug": "tehran"},
                        "city_detail": {"id": 120, "name": "تهران", "slug": "tehran"},
                        "address": "خیابان آزادی، کوچه مهر، پلاک ۱۰",
                        "created_at": "2023-12-01T10:00:00Z"
                    }
                ]
            )
        ]
    )
    def get(self, request):
        """لیست آدرس‌های کاربر"""
        addresses = self.service.get_all_addresses(request.user.id)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="ثبت آدرس جدید",
        description="""
        **نکات مهم:**
        * `province_id` و `city_id` باید شناسه معتبر از دیتابیس باشند.
        """,
        request=AddressSerializer,
        responses={201: AddressSerializer},
        examples=[
            OpenApiExample(
                'Tehran Address Example',
                summary='مثال آدرس تهران',
                description='یک نمونه آدرس معتبر برای تست.',
                value={
                    "province_id": 1,
                    "city_id": 12,
                    "address": "تهران، میدان ونک، خیابان ملاصدرا، پلاک ۱"
                },
                request_only=True,
            )
        ]
    )
    def post(self, request):
        """افزودن آدرس جدید"""
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
       
        try:
            validated_data = serializer.validated_data
        
            service_data = {
                'province_id': validated_data['province'].id,
                'city_id': validated_data['city'].id,
                'address': validated_data['address'],
            }
            new_address = self.service.add_address(request.user.id, service_data)
            return Response(AddressSerializer(new_address).data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ===== User Address Detail APIView ===== #
@extend_schema(tags=["Profile"])
class UserAddressDetailAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserAddressService()

    @extend_schema(
        summary="ویرایش آدرس",
        description="""
        برای ویرایش آدرس، شناسه آدرس را در URL وارد کنید.
        می‌توانید تمام فیلدها یا فقط فیلدهای مورد نظر را ارسال کنید (اگر متد سرویس پشتیبانی کند).
        در اینجا فرض بر ویرایش کامل (PUT) است.
        """,
        request=AddressSerializer,
        responses={200: AddressSerializer}
    )
    def put(self, request, address_id):
        """ویرایش آدرس"""
        serializer = AddressSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        service_payload = {}
        if 'province' in data: service_payload['province_id'] = data['province'].id
        if 'city' in data: service_payload['city_id'] = data['city'].id
        if 'address' in data: service_payload['address'] = data['address']
        try:
            updated_address = self.service.edit_address(request.user.id, address_id, service_payload)
            return Response(AddressSerializer(updated_address).data)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, address_id):
        """حذف آدرس"""
        try:
            self.service.remove_address(request.user.id, address_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

# ===== 1. Province List APIView ===== #
@extend_schema(tags=["Profile"])
class ProvinceListAPIView(GenericAPIView):
    """
    دریافت لیست کل استان‌ها.
    """
    # نکته: در کامنت کد قبلی نوشته بودید دسترسی آزاد، اما در کد IsAuthenticated بود.
    # اگر عمومی است، AllowAny بگذارید. من طبق کد قبلی IsAuthenticated گذاشتم.
    permission_classes = [AllowAny] 
    serializer_class = ProvinceSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserAddressService()

    @extend_schema(
        summary="لیست استان‌ها",
        responses={200: ProvinceSerializer(many=True)}
    )
    def get(self, request):
        """لیست تمام استان‌های کشور"""
        provinces = self.service.get_all_provinces()
        serializer = self.get_serializer(provinces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ===== 2. City List APIView ===== #
@extend_schema(tags=["Profile"])
class CityListAPIView(GenericAPIView):
    """
    دریافت لیست شهرها (با قابلیت فیلتر بر اساس استان).
    """
    permission_classes = [AllowAny]
    serializer_class = CitySerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserAddressService()

    @extend_schema(
        summary="لیست شهرها",
        description="برای دریافت شهرهای یک استان، پارامتر `province_id` را ارسال کنید.",
        parameters=[
            OpenApiParameter(name='province_id', description='شناسه استان', required=False, type=int)
        ],
        responses={200: CitySerializer(many=True)}
    )
    def get(self, request):
        """
        دریافت لیست شهرها. 
        اگر province_id ارسال شود، فیلتر می‌کند.
        """
        province_id = request.query_params.get('province_id')
        
        if province_id:
            cities = self.service.get_cities_by_province(province_id)
        else:
            cities = self.service.get_all_cities()
            
        serializer = self.get_serializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)