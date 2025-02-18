from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    A serializer class for the CartItem model.
    """

    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(
        source="price", max_digits=10, decimal_places=2
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity", "product_price"]
        read_only_fields = ["id"]


class CartSerializer(serializers.ModelSerializer):
    """
    A serializer class for the Cart model, including the CartItemSerializer.
    """

    cart_items = CartItemSerializer(source="cartitem_set", many=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "created_at", "updated_at", "cart_items"]
        read_only_fields = ["id", "created_at", "updated_at"]
