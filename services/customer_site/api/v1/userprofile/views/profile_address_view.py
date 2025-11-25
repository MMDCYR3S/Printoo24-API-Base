from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_spectacular.views import extend_schema

from apps.userprofile.services import UserAddressService
from ..serializers import AddressSerializer

# ===== User Address List Create APIView ===== #
@extend_schema(tags=["Profile"])
class UserAddressListCreateAPIView(APIView):
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
                data = serializer.validated_data
                clean_data = {
                    'receiver_name': data['receiver_name'],
                    'receiver_phone': data['receiver_phone'],
                    'detailed_address': data['detailed_address'],
                    'postal_code': data['postal_code'],
                    'is_default': data.get('is_default', False),
                    'province_id': data['province'].id,
                    'city_id': data['city'].id,
                }
                
                new_address = self.service.add_address(request.user.id, clean_data)
                return Response(AddressSerializer(new_address).data, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                 return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ===== User Address Detail APIView ===== #
@extend_schema(tags=["Profile"])
class UserAddressDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = UserAddressService()

    def put(self, request, address_id):
        """ویرایش آدرس"""
        allowed_fields = ['receiver_name', 'receiver_phone', 'detailed_address', 'postal_code', 'is_default', 'province_id', 'city_id']
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
