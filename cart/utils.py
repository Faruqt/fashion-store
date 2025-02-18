from .models import Cart, CartItem
from products.models import Products


def get_user_cart(user):
    return Cart.objects.get_or_create(user=user)


def get_cart_item_by_id(cart_item_id):
    return CartItem.objects.get(id=cart_item_id)


def get_product_by_id(product_id):
    return Products.objects.get(id=product_id)
