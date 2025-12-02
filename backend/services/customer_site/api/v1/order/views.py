from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.order.services import CreateOrderFromCartService
from apps.order.exceptions import (
    EmptyCartError,
    InsufficientFundsError,
    OrderCreationError
)
from .serializers import OrderSerializer

@extend_schema(tags=["Order"])
class CreateOrderView(GenericAPIView):
    """
    POST /api/v1/orders/checkout/
    Converts the user's cart into a final order.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        # 1. Validate Input (Address ID is checked here)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 'address' in validated_data is now the Address instance because of source="address"
        address_instance = serializer.validated_data.get('address')

        try:
            # 2. Execute Business Logic
            service = CreateOrderFromCartService()
            order = service.execute(
                user=request.user, 
                address=address_instance
            )
            
            # 3. Return Full Response
            # Pass request context for proper file URL generation
            output_serializer = self.get_serializer(order, context={'request': request})
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        except EmptyCartError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        except InsufficientFundsError as e:
            return Response({"error": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
            
        except Exception as e:
            return Response(
                {"error": "An error occurred while placing the order.", "detail": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
