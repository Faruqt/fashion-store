import logging
from rest_framework.response import Response
from rest_framework import status

# Getting the logger
logger = logging.getLogger("django")


def check_user_access(request, user_id, message):
    """
    A helper function to check if the user has access to the user_id.
    """

    if not request.user.is_staff and request.user.id != user_id:
        logger.error(message)
        return Response(
            {"error": message},
            status=status.HTTP_403_FORBIDDEN,
        )

    return None
