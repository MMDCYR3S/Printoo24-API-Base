from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError, PermissionDenied
from drf_spectacular.views import extend_schema

from apps.accounts.services import StaffAppService
from ..serializers import (
    StaffListSerializer, StaffCreateSerializer, StaffUpdateSerializer,
    BulkIdsSerializer, BulkRoleChangeSerializer
)
from core.domain.identity.users.exceptions import UsernameAlreadyExistsException, EmailAlreadyExistsException

# ========== STAFF MANAGEMENT VIEWS ========== #
@extend_schema(tags=["Users-Staffs"])
class StaffListCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StaffAppService()

    def get(self, request):
        """ لیست تمام پرسنل """
        try:
            staff_list = self.service.get_staff_list(request.user)
            serializer = StaffListSerializer(staff_list, many=True)
            return Response(serializer.data)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        """ استخدام کارمند جدید """
        serializer = StaffCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = self.service.create_staff(request.user, serializer.validated_data)
                return Response(StaffListSerializer(user).data, status=status.HTTP_201_CREATED)
            
            except (UsernameAlreadyExistsException, EmailAlreadyExistsException) as e:
                return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== STAFF DETAIL VIEW ========== #
@extend_schema(tags=["Users-Staffs"])
class StaffDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StaffAppService()

    def put(self, request, pk):
        """ ویرایش کارمند """
        serializer = StaffUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = self.service.update_staff(request.user, pk, serializer.validated_data)
                return Response(StaffListSerializer(user).data)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """ اخراج (حذف) کارمند """
        try:
            self.service.delete_staff(request.user, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)



# ========== BULK ACTION VIEWS ========== #
@extend_schema(tags=["Users-Staffs"])
class StaffBulkActionsView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = StaffAppService()

    def post(self, request, action):
        """
        مدیریت عملیات گروهی بر اساس پارامتر action در URL.
        actions: delete, activate, deactivate, change_role
        """
        try:
            if action == 'delete':
                serializer = BulkIdsSerializer(data=request.data)
                if serializer.is_valid():
                    result = self.service.bulk_delete(request.user, serializer.validated_data['ids'])
                    return Response(result)

            elif action == 'activate':
                serializer = BulkIdsSerializer(data=request.data)
                if serializer.is_valid():
                    count = self.service.bulk_toggle_active(request.user, serializer.validated_data['ids'], True)
                    return Response({"updated_count": count})

            elif action == 'deactivate':
                serializer = BulkIdsSerializer(data=request.data)
                if serializer.is_valid():
                    count = self.service.bulk_toggle_active(request.user, serializer.validated_data['ids'], False)
                    return Response({"updated_count": count})

            elif action == 'change_role':
                serializer = BulkRoleChangeSerializer(data=request.data)
                if serializer.is_valid():
                    count = self.service.bulk_change_role(
                        request.user, 
                        serializer.validated_data['ids'], 
                        serializer.validated_data['new_role_id']
                    )
                    return Response({"updated_count": count})
            
            else:
                return Response({"detail": "اکشن نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

