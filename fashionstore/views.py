import logging
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Getting the logger
logger = logging.getLogger("django")


@api_view(["GET"])
def welcome(request):
    """
    A simple view that returns a welcome message to the user with HTTP status 200 OK.
    """
    try:
        logger.info("Welcome message returned successfully")
        return Response(
            {"message": "Welcome to the Fashion Store API!"}, status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
