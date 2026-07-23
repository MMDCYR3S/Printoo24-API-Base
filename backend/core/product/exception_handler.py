from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler

from .exceptions import (
    ProductCategoryNotFoundException,
    InvalidProductCategoryException,
    ProductCategoryHasDependencyException,
    ProductNotFoundException,
    ProductAlreadyExistsException,
    InvalidProductDataException,
    OverRatingNumberException,
    NotBuyerException,
    ProductHasDependencyException,
)

_EXCEPTION_MAP = {
    ProductCategoryNotFoundException: status.HTTP_404_NOT_FOUND,
    ProductNotFoundException: status.HTTP_404_NOT_FOUND,
    InvalidProductCategoryException: status.HTTP_400_BAD_REQUEST,
    InvalidProductDataException: status.HTTP_400_BAD_REQUEST,
    ProductAlreadyExistsException: status.HTTP_409_CONFLICT,
    ProductCategoryHasDependencyException: status.HTTP_409_CONFLICT,
    ProductHasDependencyException: status.HTTP_409_CONFLICT,
    OverRatingNumberException: status.HTTP_400_BAD_REQUEST,
    NotBuyerException: status.HTTP_403_FORBIDDEN,
}

def product_exception_handler(exc, context):
    status_code = _EXCEPTION_MAP.get(type(exc))
    if status_code:
        return Response({"error": str(exc)}, status=status_code)
    return exception_handler(exc, context)