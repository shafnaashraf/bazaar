from rest_framework import status
from rest_framework.exceptions import APIException


class OutOfStockError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "No enough stock available"
    default_code = "out_of_stock"


