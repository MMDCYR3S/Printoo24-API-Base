from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiExample

from apps.userprofile.services import UserAddressService
from ..serializers import AddressSerializer

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
        * `postal_code` باید دقیقا ۱۰ رقم باشد.
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
                    "postal_code": "1999999999",
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
                'postal_code': validated_data['postal_code']
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
        if 'postal_code' in data: service_payload['postal_code'] = data['postal_code']

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
