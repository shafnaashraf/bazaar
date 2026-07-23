from django.urls import path
from . import views

urlpatterns = [
    path("carts/", views.CartCreateView.as_view(), name="cart-create"),
    path("carts/<uuid:cart_id>/", views.CartDetailView.as_view(), name = "cart-detail"),
    path("carts/<uuid:cart_id>/items/",views.CartItemsView.as_view(), name = "cart-items"),
    path("carts/<uuid:cart_id>/items/<int:product_id>/", views.CartItemDetailView.as_view(), name = "cart-item-details"),
         
]