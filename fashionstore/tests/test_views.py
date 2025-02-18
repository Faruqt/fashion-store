import pytest
from django.urls import reverse
from rest_framework import status


class TestViews:
    @pytest.fixture(autouse=True)
    def setup(self, client):
        self.client = client

    def test_welcome_page(self):
        url = reverse("welcome")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "Welcome to the Fashion Store API!"
