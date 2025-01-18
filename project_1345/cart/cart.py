from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound

from product.models import Product


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product_id, quantity=1, price=0):
        product_id = str(product_id)
        try:
            # Check if the product exists in the Product model
            product = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            # If the product does not exist, raise an error or handle accordingly
            raise NotFound(detail=f"Product with ID {product_id} does not exist.")

        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "price": str(Decimal(price)),
            }  # store price as Decimal
        self.cart[product_id]["quantity"] += quantity
        self.save()

    def update(self, product_id: int, quantity: int = None, price: float = None):
        product_id = str(product_id)
        updated = False
        if product_id is not None and product_id in self.cart:
            if price is not None:
                self.cart[product_id]["price"] = str(Decimal(price))
                updated = True
            if quantity is not None:
                self.cart[product_id]["quantity"] = quantity
                self.cart[product_id]["total_price"] = str(
                    Decimal(self.cart[product_id]["price"]) * quantity
                )
                updated = True
        if updated:
            self.save()

    def save(self):
        # update the session cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # mark the session as "modified", so Django will save it
        self.session.modified = True

    def remove(self, product_id) -> bool:
        product_id = str(product_id)
        if product_id in self.cart:
            if product_id in self.cart:
                del self.cart[product_id]
                self.save()
                return True
        return False

    def __iter__(self):
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]["product"] = product
        for item in cart.values():
            item["price"] = Decimal(item["price"])
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_sub_total_price(self):
        return str(
            Decimal(
                sum(
                    Decimal(item["price"]) * int(item["quantity"])
                    for item in self.cart.values()
                )
            )
        )

    def clear(self):
        """
        Remove all items from the cart.
        """
        for key in list(self.cart.keys()):  # Use list() to create a copy of keys
            del self.cart[key]
        self.save()

    def get_cart_items(self):
        # Return cart items in a structured format for API serialization
        items = []
        for product_id, item in self.cart.items():
            get_item = self.get_item(product_id=product_id, item=item)
            if get_item is None:
                continue
            items.append(get_item)

        return items

    def get_item(self, product_id: int, item=None):
        item = item or self.cart.get(str(product_id))
        if item is None:
            return None
        try:
            product = Product.objects.get(id=int(product_id))
            item_data = {
                "product_id": product_id,
                "product_name": product.name,
                "quantity": item["quantity"],
                "price": str(item["price"]),
                "total_price": str(Decimal(item["price"]) * int(item["quantity"])),
            }
            return item_data
        except Product.DoesNotExist:
            ...
        return None
