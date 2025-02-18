import pytest
from users.models import Users


@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self):
        user = Users.objects.create_user(
            first_name="Test", email="testuser@gmail.com", password="password123"
        )
        assert user.email == "testuser@gmail.com"
        assert user.check_password("password123")

    def test_super_user_creation(self):
        admin_user = Users.objects.create_super_user(
            first_name="SuperAdmin",
            email="superadminuser@gmail.com",
            password="adminpassword123",
        )
        assert admin_user.is_superuser is True
        assert admin_user.is_staff is True

    def test_user_admin_creation(self):
        admin_user = Users.objects.create_admin_user(
            first_name="Admin",
            email="adminuser@gmail.com",
            password="adminpassword123",
        )
        assert admin_user.is_staff is True
        assert admin_user.is_superuser is False
