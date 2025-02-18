import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from cart.models import Cart, CartItem
from .models import Orders, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from common.utils.pagination import CustomPageNumberPagination


# Getting the logger
logger = logging.getLogger("django")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    A view that creates an order for the logged-in user.
    """

    try:
        # Get the cart for the user
        cart = Cart.objects.get(user=request.user)

        # Create the order items
        cart_items = CartItem.objects.filter(cart=cart).all()

        # check if the cart is empty
        if not cart_items:
            logger.error(f"Cart {cart.id} is empty")
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Create the order
            order = Orders.objects.create(user=request.user, total=cart.get_total)
            for cart_item in cart_items:
                product = cart_item.product

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=cart_item.quantity,
                    price=cart_item.price,
                )

            # Clear the cart items after creating the order successfully
            cart_items.delete()

        logger.info("Order created successfully")
        return Response(
            {"message": "Order created successfully"}, status=status.HTTP_201_CREATED
        )
    except Cart.DoesNotExist:
        logger.error("Cart not found")
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_orders(request):
    """
    A view that returns a list of all orders created by all users.
    """

    try:
        paginator = CustomPageNumberPagination()
        orders = Orders.objects.all().order_by("-created_at")
        result_page = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(result_page, many=True)
        logger.info("All orders returned successfully")
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_orders(request, user_id):
    """
    A view that returns a list of all orders for a user.
    """

    try:
        if user_id != request.user.id and not request.user.is_staff:
            return Response(
                {"error": "You are not authorized to view these orders"},
                status=status.HTTP_403_FORBIDDEN,
            )
        paginator = CustomPageNumberPagination()
        orders = Orders.objects.filter(user=user_id).order_by("-created_at")

        result_page = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(result_page, many=True)
        logger.info(f"Orders returned successfully for user: {request.user.id}")
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order(request, order_id):
    """
    A view that returns a single order by ID.
    """
    try:
        order = Orders.objects.get(id=order_id)
        if order.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You are not authorized to view this order"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = OrderSerializer(order)
        logger.info(f"Order {order_id} returned successfully")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Orders.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_order_item(request, order_item_id):
    """
    A view that returns a single order item by ID.
    """
    try:
        order_item = OrderItem.objects.get(id=order_item_id)
        if order_item.order.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You are not authorized to view this order item"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = OrderItemSerializer(order_item)
        logger.info(f"Order Item {order_item_id} returned successfully")

        return Response(serializer.data, status=status.HTTP_200_OK)
    except OrderItem.DoesNotExist:
        logger.error(f"Order Item {order_item_id} not found")
        return Response(
            {"error": "Order item not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(str(e))
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
