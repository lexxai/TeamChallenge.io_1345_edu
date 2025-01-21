from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    extend_schema_view,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

from product.models import Product
from .cart import Cart
from .serializers import CartItemSerializer, CartContentSerializer, CartUpdateSerializer


@extend_schema_view(
    get=extend_schema(
        operation_id="cart_view_list",
        description="Get list of items from the cart. "
        "Or statistics info if query parameters are appended",
    ),
    post=extend_schema(),
)
class CartView(APIView):
    # serializer_class = CartContentSerializer
    serializer_class = CartItemSerializer

    def get_serializer_class(self):
        """
        Dynamically return the appropriate serializer class based on the request.
        """
        if self.request.method == "POST":
            return CartItemSerializer
        return CartContentSerializer

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
            200: CartContentSerializer(many=True),
            206: {
                "oneOf": [
                    {"type": "integer"},  # For single values like quantity or items
                    {"type": "string"},  # For total_price
                ]
            },
        },
    )
    def get(self, request, *args, **kwargs):

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
            return Response({"total_quantity": len(cart)}, status=206)

        cart_items = cart.get_cart_items()

        if get_total_items:
            return Response({"cart_items": len(cart_items)}, status=206)

        if get_total_price:
            return Response({"total_price": cart.get_sub_total_price()}, status=201)

        # Prepare the cart items data for serialization
        # cart_items_data = (
        #     [
        #         {
        #             "product_id": item["product_id"],
        #             "product_name": item["product_name"],
        #             "quantity": item["quantity"],
        #             "price": item["price"],  # Ensure price is a string or Decimal
        #             "total_price": item["total_price"],  # Calculate total price
        #         }
        #         for item in cart_items
        #     ]
        #     if cart_items
        #     else []
        # )

        # Serialize the cart items data
        # for item in cart_items:
        #     print(item)
        serializer = CartContentSerializer(cart, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=CartItemSerializer,
        responses={
            201: {
                "description": "Item added to cart",
                "content": {
                    "application/json": {
                        "examples": {
                            "item_added": {"value": {"message": "Item added to cart"}}
                        }
                    }
                },
            },
            404: {
                "description": "Product ID not found",
                "content": {
                    "application/json": {
                        "examples": {
                            "product_not_found": {
                                "value": {"product_id": "Product ID not found"}
                            }
                        }
                    }
                },
            },
            400: {
                "description": "Product ID is required",
                "content": {
                    "application/json": {
                        "examples": {
                            "product_id_required": {
                                "value": {"product_id": "Product ID is required"}
                            }
                        }
                    }
                },
            },
        },
    )
    def post(self, request):
        """ "Create an item in the cart. "
        "Note: Price is optional. If not provided, the product's price will be used. "
        "Last added price always overrides the previous price. "
        "If the product is already in the cart, its quantity will be increased by quantity. "
        "If the product does not exist, a 404 error will be returned."
        """

        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            cart = Cart(request)
            try:
                cart.add(
                    product_id=serializer.validated_data["product_id"],
                    quantity=serializer.validated_data["quantity"],
                    price=serializer.validated_data.get("price", None),
                )
                return Response(
                    {"message": "Item added to cart"}, status=status.HTTP_201_CREATED
                )
            except NotFound:
                return Response(
                    {"product_id": "Product ID not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=extend_schema(
        operation_id="cart_update_view_retrieve",
        responses={
            200: CartContentSerializer(many=False),
            400: OpenApiResponse(
                description="error request",
            ),
            404: {
                "description": '{"product_id": "Product ID not found"}',
                "content": {
                    "application/json": {
                        "examples": {
                            "item_updated": {
                                "value": {"message": "Item updated in cart"}
                            }
                        }
                    }
                },
            },
        },
    ),
    patch=extend_schema(
        request=CartUpdateSerializer,  # Serializer for request body
        responses={
            200: {
                "description": "Item updated in cart",
                "content": {
                    "application/json": {
                        "examples": {
                            "item_updated": {
                                "value": {"message": "Item updated in cart"}
                            }
                        }
                    }
                },
            },
            404: {
                "description": "Product ID not found",
                "content": {
                    "application/json": {
                        "examples": {
                            "product_not_found": {
                                "value": {"product_id": "Product ID not found"}
                            }
                        }
                    }
                },
            },
            400: {
                "description": "Product ID is required",
                "content": {
                    "application/json": {
                        "examples": {
                            "product_id_required": {
                                "value": {"product_id": "Product ID is required"}
                            }
                        }
                    }
                },
            },
        },
    ),
)
class CartGetUpdateView(APIView):
    """
    Retrieve and update or delete an item in the cart
    """

    serializer_class = CartItemSerializer

    def get(self, request, product_id: int = None, *args, **kwargs):
        """
        Retrieve an item from the cart.
        """
        if product_id is None:
            raise ValidationError({"product_id": "Product ID is required"})
        cart = Cart(request)
        item = cart.get_item(product_id)
        if item is None:
            return Response(
                {"product_id": "Product ID not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(item)

    def patch(self, request, product_id: int, *args, **kwargs):
        """Update an item in the cart"""
        if not product_id:
            return Response(
                {"product_id": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.data["product_id"] = product_id
        # Validate the request data using the serializer
        serializer = CartUpdateSerializer(data=request.data)
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
                {"product_id": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"message": "Item removed from cart"}, status=status.HTTP_204_NO_CONTENT
        )
