from rest_framework import serializers
from decimal import Decimal
from .models import Products


class ProductSerializer(serializers.ModelSerializer):
    """
    A serializer class for the Products model.
    """

    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=Decimal("0.00")
    )

    class Meta:
        model = Products
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
