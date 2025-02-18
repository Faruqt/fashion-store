"""
URL configuration for the products app.
"""

from django.urls import path
from .views import (
    get_all_products,
    get_products,
    create_product,
    get_product,
    change_product_status,
    update_product,
    delete_product,
)

urlpatterns = [
    path("", get_all_products, name="products-list"),  # GET /api/products/
    path("active", get_products, name="products-active"),  # GET /api/products/active
    path("new", create_product, name="products-create"),  # POST /api/products/new
    path(
        "<uuid:product_id>", get_product, name="product-detail"
    ),  # GET /api/products/<product_id>
    path(
        "status-toggle/<uuid:product_id>", change_product_status, name="product-status"
    ),  # PUT /api/products/status/<product_id>
    path(
        "update/<uuid:product_id>", update_product, name="update-product"
    ),  # PUT /api/products/update/<product_id>
    path(
        "delete/<uuid:product_id>", delete_product, name="delete-product"
    ),  # DELETE /api/products/delete/<product_id>
]
