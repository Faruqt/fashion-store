import logging
from rest_framework import status
from django.http import JsonResponse


# Getting the logger
logger = logging.getLogger("django")


def custom_error_404(request, exception):
    """
    A custom error handler for 404 errors.
    """
    try:
        logger.error("The requested route was not found on this server.")
        return JsonResponse(
            {"error": "The requested route was not found on this server."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(str(e))
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def custom_error_500(request):
    """
    A custom error handler for 500 errors.
    """
    try:
        logger.error("An internal server error occurred.")
        return JsonResponse(
            {"error": "An internal server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        logger.error(str(e))
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
