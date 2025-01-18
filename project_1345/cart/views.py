from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .cart import Cart
from .serializers import CartItemSerializer, CartContentSerializer


class CartView(APIView):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="quantity",
                description="If present, returns the total quantity of items in the cart.",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name="items",
                description="If present, returns the total number of distinct items in the cart.",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
            OpenApiParameter(
                name="total_price",
                description="If present, returns the total price of all items in the cart.",
                required=False,
                type=OpenApiTypes.BOOL,
            ),
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: "Bad request if parameters are invalid.",
        },
    )
    def get(self, request, product_id: int = None, *args, **kwargs):

        if product_id is not None:
            cart = Cart(request)
            item = cart.get_item(product_id)
            if item is None:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(item)

        query_params = request.query_params

        # Validate allowed parameters
        allowed_params = {"quantity", "items", "total_price"}
        invalid_params = set(query_params.keys()) - allowed_params
        if invalid_params:
            raise ValidationError(
                {"error": f"Invalid query parameters: {', '.join(invalid_params)}"}
            )

        get_total_quantity = "quantity" in query_params
        get_total_items = "items" in query_params
        get_total_price = "total_price" in query_params
        """Retrieve cart contents"""
        cart = Cart(request)

        if get_total_quantity:
            return Response({"total_quantity": len(cart)})

        cart_items = cart.get_cart_items()

        if get_total_items:
            return Response({"cart_items": len(cart_items)})

        if get_total_price:
            return Response({"total_price": cart.get_sub_total_price()})

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

    def delete(self, request, product_id: int = None, *args, **kwargs):
        """Remove an item from the cart or clear the entire cart"""
        product_id = product_id or request.data.get("product_id")
        cart = Cart(request)
        if product_id is None:
            # No product_id provided, so clear the entire cart
            cart.clear()
            return Response(
                {"message": "Cart cleared successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
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
