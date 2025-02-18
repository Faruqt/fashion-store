import pytest
from django.urls import reverse
from rest_framework import status
from users.models import Users
from products.models import Products
from cart.models import Cart, CartItem
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestCartViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            first_name="some",
            last_name="testuser",
            email="some-email",
            password="some-password123",
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
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            price=100.00,
            quantity=5,
        )

    def test_user_can_get_cart(self):
        url = reverse("cart-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"] == self.user.id
        assert len(response.data["cart_items"]) == 1

    def test_unauthenticated_user_cannot_get_cart(self):
        url = reverse("cart-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_user_can_get_cart_item(self):
        url = reverse("cart-item-detail", args=[self.cart_item.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["product"] == self.product.id
        assert response.data["product_price"] == "100.00"
        assert response.data["quantity"] == 5

    def test_unauthenticated_user_cannot_get_cart_item(self):
        url = reverse("cart-item-detail", args=[self.cart_item.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_user_cannot_add_unavailable_product_to_cart(self):
        url = reverse("cart-add", args=[self.product.id])
        data = {
            "quantity": 100,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Product is not available for sale."

    def test_user_cannot_add_quantity_more_than_stock(self):
        newest_product = Products.objects.create(
            name="New Product",
            description="New Product Description",
            price=100.00,
            stock=6,
            is_published=True,
        )
        url = reverse("cart-add", args=[newest_product.id])
        data = {
            "quantity": 100,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Not enough stock available."

    def test_user_can_add_cart_item(self):
        new_product = Products.objects.create(
            name="New Product",
            description="New Product Description",
            price=100.00,
            stock=6,
            is_published=True,
        )
        url = reverse("cart-add", args=[new_product.id])
        data = {
            "quantity": 3,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

        # refresh the product instance
        new_product.refresh_from_db()

        # check if the product stock has been reduced
        assert new_product.stock == 3

        url = reverse("cart-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"] == self.user.id
        assert len(response.data["cart_items"]) == 2

        url = reverse("cart-add", args=[new_product.id])
        data = {
            "quantity": 2,
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # refresh the product instance
        new_product.refresh_from_db()

        # check if the product stock has been reduced
        assert new_product.stock == 1

    def test_user_can_remove_cart_item(self):
        new_product = Products.objects.create(
            name="Some New Product",
            description="New Product Description",
            price=100.00,
            stock=4,
            is_published=True,
        )
        url = reverse("cart-add", args=[new_product.id])
        data = {
            "quantity": 2,
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

        # refresh the product instance
        new_product.refresh_from_db()

        # check if the product stock has been reduced
        assert new_product.stock == 2

        url = reverse("cart-remove", args=[new_product.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK

        # refresh the product instance
        new_product.refresh_from_db()

        # check if the product stock has been increased
        assert new_product.stock == 4

        url = reverse("cart-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"] == self.user.id
        assert len(response.data["cart_items"]) == 1
