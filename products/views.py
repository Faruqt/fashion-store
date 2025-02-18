import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Products
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser


# Getting the logger
logger = logging.getLogger("django")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_products(request):
    """
    A view that returns a list of all published products.
    """
    try:
        products = Products.objects.filter(is_published=True).order_by("-created_at")
        serializer = ProductSerializer(products, many=True)
        logger.info("Products returned successfully")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_products(request):
    """
    A view that returns a list of all products.
    """
    try:
        products = Products.objects.order_by("-created_at").all()
        serializer = ProductSerializer(products, many=True)
        logger.info(f"Products returned successfully for user: {request.user.id}")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_product(request, product_id):
    """
    A view that returns a single product by ID.
    """
    try:
        product = Products.objects.get(id=product_id)
        serializer = ProductSerializer(product)
        logger.info(f"Product {product_id} returned successfully")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Products.DoesNotExist:
        logger.error(f"Requested product {product_id} not found")
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_product(request):
    """
    A view that creates a new product.
    """
    try:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Product created successfully by user: {request.user.id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error("Unable to create product due to validation errors")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsAdminUser])
def change_product_status(request, product_id):
    """
    A view that publishes or unpublishes a single product by ID.
    """
    try:
        product = Products.objects.get(id=product_id)
        product.is_published = not product.is_published
        product.save()

        action = "published" if product.is_published else "unpublished"

        logger.info(
            f"Product {product_id} {action} successfully by user: {request.user.id}"
        )
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    except Products.DoesNotExist:
        logger.error("Requested Product {} not found".format(product_id))
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_product(request, product_id):
    """
    A view that updates a single product by ID.
    """
    try:
        product = Products.objects.get(id=product_id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Product {product_id} updated successfully by user: {request.user.id}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Products.DoesNotExist:
        logger.error(f"Product {product_id} not found")
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_product(request, product_id):
    """
    A view that deletes a single product by ID.
    """
    try:
        # Only allow delete if it has no orders or in a cart
        product = Products.objects.get(id=product_id)

        # Check if the product has any orders
        if product.orderitem_set.exists():
            logger.error(
                f"Product {product_id} has orders and cannot be deleted by user: {request.user.id}"
            )
            return Response(
                {"error": "Product has orders and cannot be deleted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the product is in any cart
        if product.cartitem_set.exists():
            logger.error(
                f"Product {product_id} is in a cart and cannot be deleted by user: {request.user.id}"
            )
            return Response(
                {"error": "Product is in a cart and cannot be deleted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product.delete()
        logger.info(
            f"Product {product_id} deleted successfully by user: {request.user.id}"
        )
        return Response(
            {"message": "Product deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
    except Products.DoesNotExist:
        logger.error(f"Product {product_id} not found")
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
