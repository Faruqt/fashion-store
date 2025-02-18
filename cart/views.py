import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer, CartItemSerializer
from products.models import Products
from .models import Cart, CartItem
from .utils import get_user_cart, get_cart_item_by_id, get_product_by_id


# Getting the logger
logger = logging.getLogger("django")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """
    A view that returns the cart for the logged-in user.
    """

    try:
        # Get or create the cart for the user
        cart, _ = get_user_cart(request.user)

        # Serialize the cart with the cart items
        serializer = CartSerializer(cart)
        logger.info("Cart returned successfully")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart_item(request, cart_item_id):
    """
    A view that returns a single cart item by ID.
    """
    try:
        cart_item = get_cart_item_by_id(cart_item_id)
        if cart_item.cart.user != request.user:
            return Response(
                {"error": "You are not authorized to view this cart item"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = CartItemSerializer(cart_item)
        logger.info(f"Cart Item {cart_item_id} returned successfully")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        logger.error(f"Cart Item {cart_item_id} not found")
        return Response(
            {"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    """
    A view that adds a product to the cart for the logged-in user.
    """
    try:
        quantity = request.data.get("quantity", None)
        if not quantity or int(quantity) <= 0:
            return Response(
                {"error": "Quantity must be provided and must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        quantity = int(quantity)

        # Get the product by ID
        product = get_product_by_id(product_id)

        # Ensure that the product is active
        if not product.is_published:
            return Response(
                {"error": "Product is not available for sale."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure that the product is available in stock
        if product.stock < quantity:
            return Response(
                {"error": "Not enough stock available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create the cart for the user
        cart, _ = get_user_cart(request.user)

        with transaction.atomic():
            # Check if the product is already in the cart
            cart_item, _ = CartItem.objects.get_or_create(
                cart=cart, product=product, price=product.price
            )

            # Update the quantity of the product in the cart
            cart_item.quantity += quantity
            cart_item.save()

            # Reduce the stock of the product
            product.stock -= quantity

            product.save()

        logger.info(f"Product {product_id} added to cart successfully")
        return Response(
            {"message": "Product added to cart successfully"}, status=status.HTTP_200_OK
        )
    except (ValueError, TypeError):
        return Response(
            {"error": "Quantity must be a positive integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Products.DoesNotExist:
        logger.error(f"Product {product_id} not found")
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    """
    A view that removes a product from the cart for the logged-in user.
    """
    try:
        # Get the product by ID
        product = get_product_by_id(product_id)

        # Get the cart for the user
        cart = Cart.objects.get(user=request.user)

        # Check if the product is in the cart
        cart_item = CartItem.objects.get(cart=cart, product=product)

        with transaction.atomic():
            # Increase the stock of the product
            product.stock += cart_item.quantity
            product.save()

            # Delete the product from the cart
            cart_item.delete()

        logger.info(f"Product {product_id} removed from cart successfully")
        return Response(
            {"message": "Product removed from cart successfully"},
            status=status.HTTP_200_OK,
        )
    except Products.DoesNotExist:
        logger.error(f"Product {product_id} not found")
        return Response(
            {"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Cart.DoesNotExist:
        logger.error("Cart not found")
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except CartItem.DoesNotExist:
        logger.error("Product not found in cart")
        return Response(
            {"error": "Product not found in cart"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
