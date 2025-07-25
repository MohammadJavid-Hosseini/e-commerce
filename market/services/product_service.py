from django.db.models import Min, Avg, F, ExpressionWrapper, DecimalField


def calculate_average_rating(product):
    """calculate the average rating based on reviews."""

    return product.reviews.aggregate(avg=Avg('rating')).get('avg')


def calculate_best_price(product):
    """calculate the cheapest price considering the discount."""

    annotated_queryset = product.items.filter(is_active=True).annotate(
        discounted_price=ExpressionWrapper(
            F('price') - F('discount_price'),
            output_field=DecimalField()
        )
    )

    return annotated_queryset.aggregate(
        best_price=Min('discounted_price'))['best_price']


def get_best_seller(product):
    """find the store offering the cheapset price considering discounts"""

    annotated_queryset = product.items.filter(is_active=True).annotate(
        discounted_price=ExpressionWrapper(
            F('price') - F('discount_price'),
            output_field=DecimalField()
        )
    )

    cheapest_item = annotated_queryset.order_by(
        'discounted_price').select_related('store').first()

    return cheapest_item.store if cheapest_item else None


def get_best_seller_user(product):
    """find the owner of the best store."""
    best_store = get_best_seller(product)
    return best_store.seller if best_store else None
