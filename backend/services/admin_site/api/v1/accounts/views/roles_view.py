from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError, PermissionDenied
from drf_spectacular.views import extend_schema

from apps.accounts.services import RoleAppService
from ..serializers import (
    RoleOutputSerializer, RoleInputSerializer
)

# ========== ROLE MANAGEMENT VIEWS ========== #
@extend_schema(tags=["Users-Roles"])
class RoleListCreateView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RoleAppService()

    def get(self, request):
        try:
            roles = self.service.get_role_list(request.user)
            return Response(RoleOutputSerializer(roles, many=True).data)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

    def post(self, request):
        serializer = RoleInputSerializer(data=request.data)
        if serializer.is_valid():
            try:
                role = self.service.create_role(request.user, serializer.validated_data)
                return Response(RoleOutputSerializer(role).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== ROLE DETAIL VIEW ========== #
@extend_schema(tags=["Users-Roles"])
class RoleDetailView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RoleAppService()

    def put(self, request, pk):
        serializer = RoleInputSerializer(data=request.data)
        if serializer.is_valid():
            try:
                role = self.service.update_role(request.user, pk, serializer.validated_data)
                return Response(RoleOutputSerializer(role).data)
            except ValidationError as e:
                return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            except PermissionDenied as e:
                return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            self.service.delete_role(request.user, pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
