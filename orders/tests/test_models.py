import pytest
from cart.models import Cart, CartItem
from users.models import Users
from products.models import Products
from orders.models import Orders, OrderItem


@pytest.mark.django_db
class TestOrderModel:
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
        self.cart = Cart.objects.create(user=self.user1)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            price=100.00,
            quantity=5,
        )

    def test_order_creation(self):
        order = Orders.objects.create(user=self.user1, total=200.00)
        assert order.user == self.user1

    def test_order_item_creation(self):
        order = Orders.objects.create(user=self.user2, total=200.00)
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            price=100.00,
            quantity=25,
        )
        assert order_item.order == order
        assert order_item.product == self.product
        assert order_item.price == 100.00
        assert order_item.quantity == 25
