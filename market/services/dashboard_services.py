from market.models import (
    OrderItem,
    StoreItem,
    ORDERITEM_STATUS_PENDING,
    ORDERITEM_STATUS_CONFIRMED,
    ORDERITEM_STATUS_REJECTED
)
from account.models import User
from market.serializers import OrderItemSerializer


def order_items_data(stores: list, request) -> dict:
    """return counts and rates of seller's stores"""

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
            'pending_items_ids': [item.get('id') for item in pending],
            'confirmed_items': confirmed,
            'rejected_items': rejected
            }

    return items_per_store


def seller_rates_data(user: User, stores: list) -> dict:
    """return the info on order items per store"""

    seller_stores = [store.name for store in stores]
    stores_rates = {}

    for store in stores:
        # store items info
        store_items = StoreItem.objects.filter(store=store)
        item_count = store_items.count()
        active_item_count = store_items.filter(is_active=True).count()
        # order items info
        order_items_count = OrderItem.objects.filter(store_item__store=store).count()
        pending_count = OrderItem.objects.filter(
            store_item__store=store, status=ORDERITEM_STATUS_PENDING).count()
        confirmed_count = OrderItem.objects.filter(
            store_item__store=store, status=ORDERITEM_STATUS_CONFIRMED).count()
        rejected_count = OrderItem.objects.filter(
            store_item__store=store, status=ORDERITEM_STATUS_REJECTED).count()

        stores_rates[store.name] = {
            'total_store_items': item_count,
            'approved_store_items':  active_item_count,
            'total_order_items': order_items_count,
            'pending_items': pending_count,
            'confirmed_items': confirmed_count,
            'rejected_items': rejected_count
        }

    return {
        'stores': seller_stores,
        'stores_rates': stores_rates
    }
