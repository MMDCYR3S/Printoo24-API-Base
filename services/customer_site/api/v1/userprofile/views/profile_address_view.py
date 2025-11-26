from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_spectacular.views import extend_schema

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

    def post(self, request):
        """افزودن آدرس جدید"""
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # ===== اعتبارسنجی داده ها از طرف سریالایزر ===== #
                validated_data = serializer.validated_data
                
                # ===== دریافت داده ها ===== #
                clean_data = {
                    'address': validated_data.get('address', validated_data.get('address')),
                    'postal_code': validated_data.get('postal_code'),
                    'province_id': validated_data['province'].id,
                    'city_id': validated_data['city'].id,
                }
                # ===== اضافه کردن آدرس جدید با اسفتاده از داده های اعتبارسنجی شده ===== #
                new_address = self.service.add_address(request.user.id, clean_data)
                
                return Response(AddressSerializer(new_address).data, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                 # مدیریت خطاهای سرویس
                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # مدیریت سایر خطاها
                return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ===== User Address Detail APIView ===== #
@extend_schema(tags=["Profile"])
class UserAddressDetailAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserAddressService()

    def put(self, request, address_id):
        """ویرایش آدرس"""
        allowed_fields = ['receiver_name', 'receiver_phone', 'address', 'postal_code', 'province_id', 'city_id']
        data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
        try:
            updated_address = self.service.edit_address(request.user.id, address_id, data)
            return Response(AddressSerializer(updated_address).data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, address_id):
        """حذف آدرس"""
        try:
            self.service.remove_address(request.user.id, address_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
