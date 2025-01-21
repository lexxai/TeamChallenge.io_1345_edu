from django.urls import path

from cart.api_views import CartView, CartUpdateView

urlpatterns = [
    path("", CartView.as_view(), name="cart_list"),
    path("<int:product_id>/", CartUpdateView.as_view(), name="cart_detail"),
]
