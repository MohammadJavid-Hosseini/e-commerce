from django_filters.rest_framework import FilterSet
from market.models import Product, Category, Store, StoreItem


class ProductFilter(FilterSet):
    class Meta:
        model = Product
        fields = {
            'is_active': ['exact'],
            'category__name': ['exact', 'icontains'],
        }


class CategoryFilter(FilterSet):
    class Meta:
        model = Category
        fields = {
            'is_active': ['exact'],
            'parent': ['exact'],
            'parent__name': ['exact', 'icontains']
            # FIXME: paret__name has a bug (doesn't work), fix it later
        }


class StoreFilter(FilterSet):
    class Meta:
        model = Store
        fields = {
            'address__city': ['exact', 'icontains']
        }


class StoreItemFilter(FilterSet):
    class Meta:
        model = StoreItem
        fields = {
            'is_active': ['exact'],
            'store__name': ['exact', 'icontains'],
            'stock': ['gte', 'lte'],
            'price': ['gte', 'lte'],
            'discount_price': ['gte', 'lte']
        }
