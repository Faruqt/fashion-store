import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from users.models import Users
from users.serializers import UserSerializer
from common.utils.permissions import IsSuperUser

# Getting the logger
logger = logging.getLogger("django")


@api_view(["POST"])
def create_user(request):
    """
    A view that creates a new user.
    """
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            refresh = RefreshToken.for_user(serializer.instance)
            logger.info("User created successfully")

            return Response(
                {
                    "user": serializer.data,
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsSuperUser])
def create_admin(request):
    """
    A view that creates a new admin user.
    """
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(is_staff=True)
            refresh = RefreshToken.for_user(serializer.instance)
            logger.info("Admin user created successfully")

            return Response(
                {
                    "user": serializer.data,
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login_user(request):
    """
    A view that logs in a user.
    """
    try:
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        if (
            email is None
            or password is None
            or email == ""
            or password == ""
            or email.isspace()
            or password.isspace()
        ):
            logger.error("Please provide both email and password")
            return Response(
                {"error": "Please provide both email and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = Users.objects.get(email=email)

        # check if user is still active
        if not user.is_active:
            logger.error("User account is not active")
            return Response(
                {"error": "User account is not active"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            logger.info("User logged in successfully")
            return Response(
                {
                    "message": "User logged in successfully",
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:
            logger.error("Invalid email or password")
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Users.DoesNotExist:
        logger.error("User not found")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def change_password(request):
    """
    A view that changes a user's password.
    """
    try:
        email = request.data.get("email", None)
        old_password = request.data.get("old-password", None)
        new_password = request.data.get("new-password", None)

        if (
            email is None
            or old_password is None
            or new_password is None
            or email == ""
            or old_password == ""
            or new_password == ""
            or email.isspace()
            or old_password.isspace()
            or new_password.isspace()
        ):
            logger.error("Please provide email, old password and new password")
            return Response(
                {"error": "Please provide email, old password and new password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = Users.objects.get(email=email)

        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            logger.info("Password changed successfully")
            return Response(
                {"message": "Password changed successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            logger.error("Invalid email or password")
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Users.DoesNotExist:
        logger.error("User not found")
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def refresh_token(request):
    """
    A view that refreshes a user's access token.
    """
    try:
        refresh_token = request.headers.get("Refresh-Authorization")

        if not refresh_token:
            logger.error("Refresh token is required")
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Expected format: Bearer <refresh_token>
        if refresh_token.startswith("Bearer "):
            refresh_token = refresh_token.split(" ")[1]
            if not refresh_token:
                logger.error("Refresh token is required")
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            logger.error("Invalid token format")
            return Response(
                {"error": "Invalid token format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = RefreshToken(refresh_token)
        access_token = str(token.access_token)

        logger.info("Access token refreshed successfully")
        return Response({"access_token": access_token}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    A view that logs out a user.
    """
    try:
        refresh_token = request.headers.get("Refresh-Authorization")

        if not refresh_token:
            logger.error("Refresh token is required")
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Expected format: Bearer <refresh_token>
        if refresh_token.startswith("Bearer "):
            refresh_token = refresh_token.split(" ")[1]
        else:
            logger.error("Invalid token format")
            return Response(
                {"error": "Invalid token format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a RefreshToken object
        token = RefreshToken(refresh_token)

        # Blacklist the refresh token
        token.blacklist()

        logger.info("User logged out successfully")
        return Response(
            {"message": "User logged out successfully."},
            status=status.HTTP_205_RESET_CONTENT,
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
