import logging
import uuid
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Users
from .serializers import UserSerializer
from .utils import check_user_access

# Getting the logger
logger = logging.getLogger("django")


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_users(request):
    """
    A view that returns a list of all users.
    """
    try:
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        logger.info(f"Admin user {request.user.id} successfully retrieved all users")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user(request, user_id):
    """
    A view that returns a single user by ID.
    """
    try:
        access_error = check_user_access(
            request, user_id, "User not authorized to view this user"
        )
        if access_error:
            return access_error

        user = Users.objects.get(id=user_id)
        serializer = UserSerializer(user)

        log_message = (
            f"User {user_id} returned successfully"
            if not request.user.is_staff
            else f"Admin user {request.user.id} successfully retrieved user {user_id}"
        )
        logger.info(log_message)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Users.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    """
    A view that updates a single user by ID.
    """
    try:
        access_error = check_user_access(
            request, user_id, "User not authorized to update this user"
        )
        if access_error:
            return access_error

        user = Users.objects.get(id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            log_message = (
                f"User {user_id} updated successfully"
                if not request.user.is_staff
                else f"Admin user {request.user.id} successfully updated user {user_id}"
            )
            logger.info(log_message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Users.DoesNotExist:
        logger.error("User not found")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user(request, user_id):
    """
    A view that deletes a single user by ID.
    """
    try:
        access_error = check_user_access(
            request, user_id, "User not authorized to delete this user"
        )
        if access_error:
            return access_error

        user = Users.objects.get(id=user_id)
        # remove sensitive data
        user.first_name = "Deleted"
        user.last_name = "User"

        # Generate a random string to replace the email
        random_email = f"{uuid.uuid4().hex[:10]}@deleted.com"
        user.email = f"{random_email}"
        user.is_active = False

        # Save the user
        user.save()
        log_message = (
            f"User {user_id} deleted successfully"
            if not request.user.is_staff
            else f"Admin user {request.user.id} successfully deleted user {user_id}"
        )
        logger.info(log_message)
        return Response(
            {"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
    except Users.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
