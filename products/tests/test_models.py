import pytest
from products.models import Products


@pytest.mark.django_db
class TestProductModel:
    def test_product_creation(self):
        product = Products.objects.create(
            name="Test Product",
            description="Test Product Description",
            price=100.00,
            stock=10,
        )
        assert product.name == "Test Product"
        assert product.description == "Test Product Description"
        assert product.price == 100.00
        assert product.stock == 10
        assert product.is_published is False
