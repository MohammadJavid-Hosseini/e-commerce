from market.models import (
    OrderItem,
    StoreItem,
    ORDERITEM_STATUS_PENDING,
    ORDERITEM_STATUS_CONFIRMED,
    ORDERITEM_STATUS_REJECTED
)
from market.custom_exceptions import (
    OrderItemCannotConfirmError,
    OutOfStockError
)


def confirm_order_items(order_items: list):
    """confirm multiple order items with stock checking"""

    to_update_store_items = []
    to_update_items = []

    # check object status; pending
    for order_item in order_items:
        if order_item.status != ORDERITEM_STATUS_PENDING:
            raise OrderItemCannotConfirmError(
                f"order item {order_item.id} cannot ocnfirm; it's already {order_item.status}")

        # check stock
        quantity = order_item.quantity
        stock = order_item.store_item.stock
        if quantity > stock:
            order_item.status = ORDERITEM_STATUS_REJECTED
            order_item.save()
            raise OutOfStockError(
                "order_item rejected because of lack of stock")

        # reserve quantity for customer; change status to confirmed
        order_item.store_item.stock -= order_item.quantity
        order_item.status = ORDERITEM_STATUS_CONFIRMED

        to_update_store_items.append(order_item.store_item)
        to_update_items.append(order_item)

    # bulk updates
    StoreItem.objects.bulk_update(to_update_store_items, ['stock'])
    OrderItem.objects.bulk_update(to_update_items, ['status'])

    return order_items


def reject_order_items(order_items: list):
    """seller can reject order_items manually"""

    to_update = []
    # check object status; pending
    # OPTIMIZE: the operation should not stop on the first problem here
    for order_item in order_items:
        if order_item.status != ORDERITEM_STATUS_PENDING:
            raise OrderItemCannotConfirmError(
                f"cannot reject item {order_item.id}; it's already {order_item.status}")

        # update status
        order_item.status = ORDERITEM_STATUS_REJECTED
        to_update.append(order_item)

    # bulk update
    OrderItem.objects.bulk_update(to_update, ['status'])

    return order_items
