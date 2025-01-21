from django.urls import path

from cart.api_views import CartView, CartGetUpdateView

urlpatterns = [
    path("", CartView.as_view(), name="cart_list"),
    path("<int:product_id>/", CartGetUpdateView.as_view(), name="cart_detail"),
]
