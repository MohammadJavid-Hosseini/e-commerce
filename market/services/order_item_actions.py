from market.models import (
    ORDERITEM_STATUS_PENDING,
    ORDERITEM_STATUS_CONFIRMED,
    ORDERITEM_STATUS_REJECTED
)
from market.custom_exceptions import (
    OrderItemCannotConfirmError,
    OutOfStockError
)


def confirm_order_item(order_item):
    """a service to confirm an order_item with stock checking"""

    # check object status; pending
    if order_item.status != ORDERITEM_STATUS_PENDING:
        raise OrderItemCannotConfirmError(
            f"order item cannot ocnfirm; it's already {order_item.status}")

    # check stock
    quantity = order_item.quantity
    stock = order_item.store_item.stock
    if quantity > stock:
        order_item.status = ORDERITEM_STATUS_REJECTED
        order_item.save()
        raise OutOfStockError("order_item rejected because of lack of stock")

    # reserve quantity for customer; status -> confirmed
    store_item = order_item.store_item
    store_item.stock -= order_item.quantity
    store_item.save()
    order_item.status = ORDERITEM_STATUS_CONFIRMED
    order_item.save()

    return order_item


def reject_order_item(order_item):
    """seller can reject the order_item manually"""

    # check object status; pending
    if order_item.status != ORDERITEM_STATUS_PENDING:
        raise OrderItemCannotConfirmError(
            f"cannot reject this item; it's already {order_item.status}")

    # update status
    order_item.status = ORDERITEM_STATUS_REJECTED
    order_item.save()

    return order_item
