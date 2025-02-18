"""
URL configuration for the auth app.
"""

from django.urls import path
from .views import (
    login_user,
    create_user,
    create_admin,
    logout_user,
    refresh_token,
    change_password,
)

urlpatterns = [
    path("login", login_user, name="auth-login"),
    path("create-user", create_user, name="auth-create-user"),
    path("create-admin", create_admin, name="auth-create-admin"),
    path("logout", logout_user, name="auth-logout"),
    path("refresh-token", refresh_token, name="auth-refresh-token"),
    path("change-password", change_password, name="auth-change-password"),
]
