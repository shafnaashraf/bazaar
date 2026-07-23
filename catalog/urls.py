from django.urls import path
from . import views

urlpatterns = [
    path("categories/", views.CategoryListCreateView.as_view(), name="category-list"),
    path("products/", views.ProductListCreateView.as_view(), name="product-list"),
    path("products/<int:product_id>/", views.ProductDetailView.as_view(), name="product-detail"),

]