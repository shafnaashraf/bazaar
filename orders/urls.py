from django.urls import path

from . import views

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("orders/<uuid:reference>/", views.OrderDetailView.as_view(), name="order-detail"),
]