from market.models import (
    OrderItem,
    ORDERITEM_STATUS_PENDING,
    ORDERITEM_STATUS_CONFIRMED,
    ORDERITEM_STATUS_REJECTED
)
from market.serializers import OrderItemSerializer


def order_items_data(stores: list, request) -> dict:
    items_per_store = {}

    for store in stores:
        items_qs = OrderItem.objects.filter(store_item__store=store)

        pending_qs = items_qs.filter(status=ORDERITEM_STATUS_PENDING).all()
        pending = OrderItemSerializer(
            pending_qs, many=True, context={'request': request}).data

        confirmed_qs = items_qs.filter(status=ORDERITEM_STATUS_CONFIRMED).all()
        confirmed = OrderItemSerializer(
            confirmed_qs, many=True, context={'request': request}).data

        rejected_qs = items_qs.filter(status=ORDERITEM_STATUS_REJECTED).all()
        rejected = OrderItemSerializer(
            rejected_qs, many=True, context={'request': request}).data

        items_per_store[store.name] = {
            'pending_items': pending,
            'pending_ids': [item.get('id') for item in pending],
            'confirmed_items': confirmed,
            'rejected_items': rejected
            }

    return items_per_store
