from rest_framework import status
from rest_framework.exceptions import APIException


class OutOfStockError(APIException):
    '''Throw when there is no enough stock available'''
    status_code = status.HTTP_409_CONFLICT
    default_detail = "No enough stock available"
    default_code = "out_of_stock"


class EmptyCartError(APIException):
    '''thow if the cart doesn't have any products t be checked out'''
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Empty cart cannot be checked out"
    default_code = "empy_cart"

class InvalidDiscountError(APIException):
    '''thow if the user uses an invlaid discount code'''
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The discount code is invalid or has expired."
    default_code = "invalid_discount"