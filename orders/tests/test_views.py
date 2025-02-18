import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.models import Users
from products.models import Products
from cart.models import Cart, CartItem
from orders.models import Orders, OrderItem


@pytest.mark.django_db
class TestOrderViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            first_name="some",
            last_name="testuser",
            email="some-email",
            password="some-password123",
        )
        self.user2 = Users.objects.create_user(
            first_name="another",
            last_name="testuser",
            email="another-email",
            password="another-password123",
        )
        self.admin_user = Users.objects.create_admin_user(
            first_name="some",
            last_name="adminuser",
            email="some-admin-email",
            password="some-admin-password123",
        )
        self.product = Products.objects.create(
            name="Test Product",
            description="Test Product Description",
            price=100.00,
            stock=10,
        )
        self.product2 = Products.objects.create(
            name="Test Product 2",
            description="Test Product Description 2",
            price=200.00,
            stock=10,
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            price=100.00,
            quantity=5,
        )
        self.order = Orders.objects.create(user=self.user, total=200.00)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            price=100.00,
            quantity=5,
        )

    def test_admin_can_get_all_orders(self):
        url = reverse("orders-list")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_non_admin_cannot_get_all_orders(self):
        url = reverse("orders-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_user_can_get_orders(self):
        url = reverse("orders-user", args=[self.user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_unauthenticated_user_cannot_get_orders(self):
        url = reverse("orders-user", args=[self.user.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_user_cannot_get_orders_of_another_user(self):
        url = reverse("orders-user", args=[self.user2.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"] == "You are not authorized to view these orders"

    def test_admin_can_get_orders_of_any_user(self):
        url = reverse("orders-user", args=[self.user.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_user_can_get_order_detail(self):
        url = reverse("order-detail", args=[self.order.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total"] == "200.00"

    def test_unauthenticated_user_cannot_get_order_detail(self):
        url = reverse("order-detail", args=[self.order.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_user_cannot_get_another_users_order_detail(self):
        url = reverse("order-detail", args=[self.order.id])
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"] == "You are not authorized to view this order"

    def test_admin_can_get_any_order_detail(self):
        url = reverse("order-detail", args=[self.order.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total"] == "200.00"

    def test_user_can_view_order_item_details(self):
        url = reverse("order-item-detail", args=[self.order_item.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["product"] == self.product.id

    def test_unauthenticated_user_cannot_view_order_item_details(self):
        url = reverse("order-item-detail", args=[self.order_item.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_user_cannot_view_order_item_details_of_another_user(self):
        url = reverse("order-item-detail", args=[self.order_item.id])
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["error"] == "You are not authorized to view this order item"
        )

    def test_admin_can_view_any_order_item_details(self):
        url = reverse("order-item-detail", args=[self.order_item.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["product"] == self.product.id

    def test_user_can_create_order(self):
        url = reverse("orders-create")
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"] == "Cart not found"

        cart = Cart.objects.create(user=self.user2)
        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Cart is empty"

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            price=self.product.price,
            quantity=2,
        )
        CartItem.objects.create(
            cart=cart,
            product=self.product2,
            price=self.product2.price,
            quantity=3,
        )

        # assert that the cart items are created
        assert CartItem.objects.filter(cart=cart).count() == 2

        url = reverse("orders-create")
        response = self.client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # refresh the cartitems instance
        cart_items = CartItem.objects.filter(cart=cart)

        # Check if the cart items are deleted after creating the order
        assert cart_items.count() == 0

        # Check if the order is created
        assert Orders.objects.filter(user=self.user2).count() == 1

        # check if the order items are created
        assert OrderItem.objects.filter(order__user=self.user2).count() == 2
