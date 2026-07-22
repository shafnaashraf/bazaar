from django.shortcuts import render

from .models import Cart, CartItem
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CartSerializer, AddItemSerializer, UpdateItemSerializer
from . import service
from drf_spectacular.utils import extend_schema


class CartCreateView(APIView):
    def post(self, request):
        cart = service.create_cart()
        return Response(CartSerializer(cart).data , status = status.HTTP_201_CREATED)
    

class CartDetailView(APIView):
    def get(self , request, cart_id):
        return Response(CartSerializer(service.get_cart(cart_id)).data)
    
class CartItemsView(APIView):
    @extend_schema(request=AddItemSerializer, responses=CartSerializer)
    def post(self, request, cart_id):
        cart = service.get_cart(cart_id)
        payload = AddItemSerializer(data = request.data)
        payload.is_valid(raise_exception= True)
        service.add_item(cart, payload.validated_data["product"],
                         payload.validated_data["quantity"])
        return Response(CartSerializer(cart).data)

class CartItemDetailView(APIView):
    def patch(self, request , cart_id, product_id):
        cart = service.get_cart(cart_id)
        payload = UpdateItemSerializer(data = request.data)
        payload.is_valid(raise_exception=True)
        service.update_item(cart , product_id, payload.validated_data["quantity"])
        return Response(CartSerializer(cart).data)

    def delete(self, request, cart_id, product_id):
        cart = service.get_cart(cart_id)
        service.remove_item(cart, product_id)
        return Response(CartSerializer(cart).data)

                        


# Create your views here.
