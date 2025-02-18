from django.db import models
from decimal import Decimal
from common.models import UUIDModel


class Orders(UUIDModel):
    """
    A model that represents an order in the system
    """

    user = models.ForeignKey("users.Users", on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_total(self):
        """
        Calculate the total price of all items in the order
        """
        total = Decimal("0.00")

        for item in self.orderitem_set.all():
            total += item.price * item.quantity

        return total.quantize(Decimal("0.00"))

    def __str__(self):
        return f"Order: {self.user}"


class OrderItem(UUIDModel):
    """
    A model that represents an order item in the system
    """

    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Products", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem: {self.order} - {self.product}"
