from rest_framework import serializers
from .models import Orders, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    A serializer class for the OrderItem model.
    """

    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(
        source="price", max_digits=10, decimal_places=2
    )

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "product_price"]
        read_only_fields = ["id"]


class OrderSerializer(serializers.ModelSerializer):
    """
    A serializer class for the Orders model, including the OrderItemSerializer.
    """

    order_items = OrderItemSerializer(source="orderitem_set", many=True)

    class Meta:
        model = Orders
        fields = ["id", "user", "total", "created_at", "updated_at", "order_items"]
        read_only_fields = ["id", "created_at", "updated_at"]
