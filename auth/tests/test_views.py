import pytest
from django.urls import reverse
from rest_framework import status
from users.models import Users


@pytest.mark.django_db
class TestAuthViews:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.client = client
        self.user = Users.objects.create_user(
            first_name="some",
            last_name="testuser",
            email="some-email",
            password="some-password123",
        )
        self.super_user = Users.objects.create_super_user(
            first_name="some",
            last_name="adminuser",
            email="some-admin-email",
            password="some-admin-password123",
        )

    def test_user_login_sucess(self):
        url = reverse("auth-login")
        data = {"email": "some-email", "password": "some-password123"}
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data

    def test_user_login_failure(self):
        url = reverse("auth-login")
        data = {"email": "some-other-email", "password": "wrong-password"}
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.data
        assert response.data["error"] == "User not found"

    def test_user_registration(self):
        url = reverse("auth-create-user")
        data = {
            "first_name": "newuser",
            "password": "newpassword123",
            "email": "newuser@example.com",
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["first_name"] == "newuser"
        assert response.data["user"]["is_staff"] is False
        assert response.data["user"]["is_superuser"] is False
        assert "access_token" in response.data
        assert "refresh_token" in response.data

    def test_admin_registration_fails_without_authentication(self):
        url = reverse("auth-create-admin")
        data = {
            "first_name": "adminuser",
            "password": "adminpassword123",
            "email": "adminuser@example.com",
        }

        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["detail"] == "Authentication credentials were not provided."
        )

    def test_admin_registration_fails_without_superuser_permissions(self):
        url = reverse("auth-login")
        data = {"email": "some-email", "password": "some-password123"}
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data

        user_token = response.data["access_token"]

        url = reverse("auth-create-admin")
        data = {
            "first_name": "adminuser",
            "password": "adminpassword123",
            "email": "adminuser@example.com",
        }

        response = self.client.post(
            url, data, format="json", headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            response.data["detail"]
            == "You do not have permission to perform this action."
        )

    def test_admin_registration_succeeds_with_superuser_permissions(self):
        url = reverse("auth-login")
        data = {"email": "some-admin-email", "password": "some-admin-password123"}
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data
        assert "refresh_token" in response.data

        admin_token = response.data["access_token"]

        url = reverse("auth-create-admin")
        data = {
            "first_name": "regular",
            "last_name": "admin",
            "password": "adminpassword123",
            "email": "some-regular-admin@example.com",
        }

        response = self.client.post(
            url,
            data,
            format="json",
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["first_name"] == "regular"
        assert response.data["user"]["is_staff"] is True
        assert response.data["user"]["is_superuser"] is False
        assert "access_token" in response.data
        assert "refresh_token" in response.data

    def test_user_change_password_fails(self):
        url = reverse("auth-change-password")
        data = {
            "email": "some-emails",
            "old-password": "some-password123",
            "new-password": "",
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert (
            response.data["error"]
            == "Please provide email, old password and new password"
        )

    def test_user_change_password_successfully(self):
        url = reverse("auth-create-user")
        data = {
            "first_name": "some-newuser",
            "password": "some-newpassword123",
            "email": "some-newuser@example.com",
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["first_name"] == "some-newuser"

        data = {
            "email": "some-newuser@example.com",
            "old-password": "some-newpassword123",
            "new-password": "new-password123",
        }
        url = reverse("auth-change-password")
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert response.data["message"] == "Password changed successfully"

    def test_user_refresh_token_fails(self):
        url = reverse("auth-refresh-token")
        response = self.client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert response.data["error"] == "Refresh token is required."

    def test_user_refresh_token_success(self):
        url = reverse("auth-login")
        data = {"email": "some-email", "password": "some-password123"}
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data

        user_refresh_token = response.data["refresh_token"]

        url = reverse("auth-refresh-token")
        response = self.client.post(
            url, headers={"Refresh-Authorization": f"Bearer {user_refresh_token}"}
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data

    def test_user_logout_fails(self):
        url = reverse("auth-login")
        data = {"email": "some-email", "password": "some-password123"}
        response = self.client.post(
            url,
            data,
            format="json",
        )
        user_token = response.data["access_token"]

        logout_url = reverse("auth-logout")
        response = self.client.post(
            logout_url, headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert response.data["error"] == "Refresh token is required."

    def test_user_logout_success(self):
        url = reverse("auth-login")
        data = {"email": "some-email", "password": "some-password123"}
        response = self.client.post(
            url,
            data,
            format="json",
        )

        user_token = response.data["access_token"]

        logout_url = reverse("auth-logout")
        response = self.client.post(
            logout_url,
            headers={
                "Authorization": f"Bearer {user_token}",
                "Refresh-Authorization": f"Bearer {response.data['refresh_token']}",
            },
        )
        assert response.status_code == status.HTTP_205_RESET_CONTENT
        assert "message" in response.data
        assert response.data["message"] == "User logged out successfully."
