from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from cart import service as cart_service

from . import service
from .models import Order
from .serializers import CheckoutSerializer, OrderSerializer
from drf_spectacular.utils import extend_schema



class CheckoutView(APIView):
    @extend_schema(request=CheckoutSerializer, responses=OrderSerializer)
    def post(self, request):
        payload = CheckoutSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        cart = cart_service.get_cart(payload.validated_data["cart"])
        order = service.checkout(
            cart, discount_code=payload.validated_data.get("discount_code") or None)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    def get(self, request, reference):
        order = get_object_or_404(Order, reference=reference)
        return Response(OrderSerializer(order).data)
