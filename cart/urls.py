"""
URL configuration for the cart app.
"""

from django.urls import path
from .views import *

urlpatterns = [
    path("", get_cart, name="cart-list"),  # GET /api/cart/
    path(
        "<uuid:cart_item_id>", get_cart_item, name="cart-item-detail"
    ),  # GET /api/cart/<cart_item_id>
    path(
        "add/<uuid:product_id>", add_to_cart, name="cart-add"
    ),  # POST /api/cart/add/<product_id>
    path(
        "remove/<uuid:product_id>", remove_from_cart, name="cart-remove"
    ),  # DELETE /api/cart/remove/<product_id>
]
