from django.urls import path

from cart.views import CartView

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("<int:product_id>/", CartView.as_view(), name="cart_param"),
]
