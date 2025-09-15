from django.db.models import Min, Avg, F, ExpressionWrapper, DecimalField
from django.db.models.functions import Coalesce


def calculate_average_rating(product):
    """calculate the average rating based on reviews."""

    return product.reviews.aggregate(avg=Avg('rating')).get('avg')


def calculate_best_price(product):
    """calculate the cheapest price considering the discount."""

    annotated_queryset = product.items.filter(is_active=True).annotate(
        discounted_price=ExpressionWrapper(
            F('price') - Coalesce(F('discount_price'), 0),  # Use Coalesce to handle None values
            output_field=DecimalField()
        )
    )

    return annotated_queryset.aggregate(
        best_price=Min('discounted_price'))['best_price']


def get_best_seller_item(product):
    """find the store offering the cheapest price considering discounts.

    Returns the StoreItem instance representing the best seller, or None.
    """

    annotated_queryset = product.items.filter(is_active=True).annotate(
        discounted_price=ExpressionWrapper(
            F('price') - Coalesce(F('discount_price'), 0),
            output_field=DecimalField()
        )
    ).select_related('store', 'store__seller')

    cheapest_item = annotated_queryset.order_by('discounted_price').first()

    return cheapest_item if cheapest_item else None


def get_best_seller_user(product):
    """find the owner of the best store."""
    best_item = get_best_seller_item(product)
    return best_item.store.seller if best_item else None
