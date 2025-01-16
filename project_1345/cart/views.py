from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .cart import Cart
from .serializers import CartItemSerializer, CartContentSerializer


class CartView(APIView):
    def get(self, request):
        """Retrieve cart contents"""
        cart = Cart(request)
        cart_items = cart.get_cart_items()
        serializer = CartContentSerializer(cart_items.items(), many=True)
        return Response(serializer.data)

    def post(self, request):
        """Add an item to the cart"""
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart(request)
            cart.add(
                product_id=serializer.validated_data["product_id"],
                quantity=serializer.validated_data["quantity"],
                price=serializer.validated_data.get("price", 0),
            )
            return Response(
                {"message": "Item added to cart"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Remove an item from the cart"""
        product_id = request.data.get("product_id")
        if product_id:
            cart = Cart(request)
            cart.remove(product_id)
            return Response(
                {"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )
