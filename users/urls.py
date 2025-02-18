"""
URL configuration for the users app.
"""

from django.urls import path
from .views import *

urlpatterns = [
    path("", get_users, name="users-list"),  # GET /api/users/
    path("<uuid:user_id>", get_user, name="user-detail"),  # GET /api/users/<user_id>
    path(
        "update/<uuid:user_id>", update_user, name="update-user"
    ),  # PUT /api/users/update/<user_id>
    path(
        "delete/<uuid:user_id>", delete_user, name="delete-user"
    ),  # DELETE /api/users/delete/<user_id>
]
