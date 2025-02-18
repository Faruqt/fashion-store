import pytest
from cart.models import Cart, CartItem
from users.models import Users
from products.models import Products


@pytest.mark.django_db
class TestCartModel:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user1 = Users.objects.create_user(
            first_name="Test",
            email="testuser@gmail.com",
            password="password123",
        )
        self.user2 = Users.objects.create_user(
            first_name="Test2",
            email="testuser2@gmail.com",
            password="password123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            description="Test Product Description",
            price=100.00,
            stock=10,
        )

    def test_cart_creation(self):
        cart = Cart.objects.create(user=self.user1)
        assert cart.user == self.user1

    def test_cart_item_creation(self):
        cart = Cart.objects.create(user=self.user2)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            price=100.00,
            quantity=25,
        )
        assert cart_item.cart == cart
        assert cart_item.product == self.product
        assert cart_item.price == 100.00
        assert cart_item.quantity == 25
