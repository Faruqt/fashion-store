import pytest
import uuid
from django.urls import reverse
from rest_framework import status
from users.models import Users
from products.models import Products
from orders.models import Orders, OrderItem
from cart.models import CartItem, Cart
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestProductViews:
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

    def test_non_admin_cannot_create_product(self):
        url = reverse("products-create")
        self.client.force_authenticate(user=self.user)
        data = {
            "name": "Test Product",
            "description": "Test Product Description",
            "price": 100.00,
            "stock": 10,
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_admin_can_create_product(self):
        url = reverse("products-create")
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Test Product",
            "description": "Test Product Description",
            "price": 100.00,
            "stock": 10,
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Product"
        assert response.data["description"] == "Test Product Description"
        assert response.data["price"] == "100.00"
        assert response.data["stock"] == 10
        assert response.data["is_published"] is False

    def test_non_admin_cannot_update_product(self):
        url = reverse("update-product", args=[self.product.id])
        self.client.force_authenticate(user=self.user)
        data = {"name": "Updated Test Product"}
        response = self.client.put(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_admin_can_update_product(self):
        url = reverse("update-product", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Updated Test Product",
            "description": "Updated Test Product Description",
            "price": 200.00,
            "stock": 20,
        }
        response = self.client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Test Product"
        assert response.data["description"] == "Updated Test Product Description"
        assert response.data["price"] == "200.00"
        assert response.data["stock"] == 20

    def test_non_admin_cannot_change_product_status(self):
        url = reverse("product-status", args=[self.product.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_admin_can_change_product_status(self):
        url = reverse("product-status", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["is_published"] is True
        response = self.client.patch(url)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["is_published"] is False

    def test_non_admin_cannot_delete_a_product(self):
        url = reverse("delete-product", args=[self.product.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_admin_can_delete_a_product(self):
        new_product = Products.objects.create(
            name="Test Product 2",
            description="Test Product Description 2",
            price=100.00,
            stock=10,
        )
        assert Products.objects.count() == 2
        url = reverse("delete-product", args=[new_product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Products.objects.count() == 1

    def test_admin_cannot_delete_a_product_that_does_not_exist(self):
        url = reverse("delete-product", args=[uuid.uuid4()])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_cannot_delete_a_product_with_orders(self):
        order = Orders.objects.create(user=self.user, total=self.product.price)
        OrderItem.objects.create(
            order=order, product=self.product, quantity=1, price=self.product.price
        )
        assert Orders.objects.count() == 1
        url = reverse("delete-product", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Product has orders and cannot be deleted"

    def test_admin_cannot_delete_a_product_in_a_cart(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart, product=self.product, quantity=1, price=self.product.price
        )
        assert CartItem.objects.count() == 1
        url = reverse("delete-product", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Product is in a cart and cannot be deleted"

    def test_non_admin_cannot_view_all_products(self):
        url = reverse("products-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_admin_can_view_all_products(self):
        url = reverse("products-list")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_non_admin_can_view_active_products_list(self):
        url = reverse("product-status", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["is_published"] is True

        url = reverse("products-active")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        url = reverse("product-status", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["is_published"] is False

    def test_admin_can_view_active_products_list(self):
        url = reverse("product-status", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["is_published"] is True

        url = reverse("products-active")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        url = reverse("product-status", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["is_published"] is False

    def test_non_admin_can_view_single_product(self):
        url = reverse("product-detail", args=[self.product.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == self.product.name

    def test_admin_can_view_single_product(self):
        url = reverse("product-detail", args=[self.product.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == self.product.name
