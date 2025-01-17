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

        # Prepare the cart items data for serialization
        cart_items_data = (
            [
                {
                    "product_id": item["product_id"],
                    "product_name": item["product_name"],
                    "quantity": item["quantity"],
                    "price": item["price"],  # Ensure price is a string or Decimal
                    "total_price": item["total_price"],  # Calculate total price
                }
                for item in cart_items
            ]
            if cart_items
            else []
        )

        # Serialize the cart items data
        serializer = CartContentSerializer(cart_items_data, many=True)
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
        """Remove an item from the cart or clear the entire cart"""
        product_id = request.data.get("product_id")

        cart = Cart(request)

        if product_id:
            # Remove the specific product from the cart
            cart.remove(product_id)
            return Response(
                {"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            # No product_id provided, so clear the entire cart
            cart.clear()
            return Response(
                {"message": "Cart cleared successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
