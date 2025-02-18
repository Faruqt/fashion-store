"""
URL configuration for the orders app.
"""

from django.urls import path
from .views import get_all_orders, get_orders, create_order, get_order, get_order_item

urlpatterns = [
    path("all", get_all_orders, name="orders-list"),  # GET /api/orders/all
    path(
        "all/<uuid:user_id>", get_orders, name="orders-user"
    ),  # GET /api/orders/all/<user_id>
    path(
        "all/<uuid:user_id>", get_orders, name="orders-all"
    ),  # GET /api/orders/all/<user_id>
    path("new", create_order, name="orders-create"),  # POST /api/orders/new
    path(
        "<uuid:order_id>", get_order, name="order-detail"
    ),  # GET /api/orders/<order_id>
    path(
        "item/<uuid:order_item_id>", get_order_item, name="order-item-detail"
    ),  # GET /api/orders/item/<order_item_id>
]
