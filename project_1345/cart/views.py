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

    def put(self, request, product_id: int, *args, **kwargs):
        """Update an item in the cart"""
        if not product_id:
            return Response(
                {"message": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.data["product_id"] = product_id
        # Validate the request data using the serializer
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            # Initialize the cart
            cart = Cart(request)

            # Check if the product exists in the cart
            if str(product_id) not in cart.cart:
                return Response(
                    {"message": "Product not found in cart"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Update the item in the cart
            cart.cart[str(product_id)]["quantity"] = serializer.validated_data[
                "quantity"
            ]
            if "price" in serializer.validated_data:
                cart.cart[str(product_id)]["price"] = str(
                    serializer.validated_data["price"]
                )

            # Save the updated cart
            cart.save()

            return Response(
                {"message": "Item updated in cart"},
                status=status.HTTP_200_OK,
            )

        # Return validation errors if serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, product_id: int):
        """Update an item in the cart"""
        self.put(request, product_id)

    def delete(self, request):
        """Remove an item from the cart or clear the entire cart"""
        product_id = request.data.get("product_id")

        cart = Cart(request)

        if product_id:
            # Remove the specific product from the cart
            result = cart.remove(product_id)
            if not result:
                return Response(
                    {"message": "Item not found in cart"},
                    status=status.HTTP_404_NOT_FOUND,
                )
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
