import pytest
from django.urls import reverse
from rest_framework import status
from users.models import Users
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUserViews:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            first_name="some",
            last_name="testuser",
            email="some-email",
            password="some-password123",
        )
        self.another_user = Users.objects.create_user(
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

    def test_non_admin_cannot_get_users_list(self):
        url = reverse("users-list")
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_admin_can_get_users_list(self):
        url = reverse("users-list")
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_non_authenticated_user_cannot_get_user_detail(self):
        url = reverse("user-detail", args=[self.user.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_authenticated_user_can_get_own_user_detail(self):
        url = reverse("user-detail", args=[self.user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email

    def test_user_cannot_get_another_users_detail(self):
        url = reverse("user-detail", args=[self.another_user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"] == "User not authorized to view this user"

    def test_admin_can_get_any_users_detail(self):
        url = reverse("user-detail", args=[self.user.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email

    def user_cannot_update_another_user(self):
        url = reverse("user-detail", args=[self.another_user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, {"first_name": "new-name"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"] == "User not authorized to update this user"

    def test_user_can_update_own_detail(self):
        url = reverse("update-user", args=[self.user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, {"first_name": "new-name"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "new-name"

    def test_admin_can_update_own_detail(self):
        url = reverse("update-user", args=[self.admin_user.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(url, {"first_name": "newer-name"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "newer-name"

    def test_admin_can_update_any_user(self):
        url = reverse("update-user", args=[self.user.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.put(url, {"last_name": "newer-last-name"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["last_name"] == "newer-last-name"

    def test_user_cannot_delete_another_user(self):
        url = reverse("delete-user", args=[self.another_user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"] == "User not authorized to delete this user"

    def test_user_can_delete_own_user(self):
        url = reverse("delete-user", args=[self.user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Refresh the user object
        self.user.refresh_from_db()
        assert self.user.is_active is False
        assert self.user.first_name == "Deleted"
        assert self.user.last_name == "User"

    def test_admin_can_delete_any_user(self):
        url = reverse("delete-user", args=[self.user.id])
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Refresh the user object
        self.user.refresh_from_db()
        assert self.user.is_active is False
        assert self.user.first_name == "Deleted"
        assert self.user.last_name == "User"
