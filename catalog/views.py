from django.shortcuts import render

from .models import Category
from . import service
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import ProductSerializer, CategorySerializer

class CategoryListCreateView(APIView):
    def get(self,request):
        return Response(CategorySerializer(Category.objects.all(),many =True).data)
    
    def post(self, request):
        s = CategorySerializer(data = request.data)
        s.is_valid(raise_exception= True)
        s.save()
        return Response(s.data, status= status.HTTP_201_CREATED)



class ProductListCreateView(APIView):
    def get(self, request):
        return Response(service.list_products())
    
    def post(self, request):
        s = ProductSerializer(data= request.data)
        s.is_valid(raise_exception=True)
        product = service.create_product(s.validated_data)
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
    

class ProductDetailView(APIView):
    def get(self, request , product_id):
        return Response(ProductSerializer(service.get_product(product_id)).data)

    def put(self, request, product_id):
        return self._update(request, product_id, partial=False)

    def patch(self, request, product_id):
        return self._update(request, product_id, partial=True)

    def _update(self, request, product_id, partial):
        product = service.get_product(product_id)
        s = ProductSerializer(product, data=request.data, partial=partial)
        s.is_valid(raise_exception=True)
        updated = service.update_product(product, s.validated_data)
        return Response(ProductSerializer(updated).data)