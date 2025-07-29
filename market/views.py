from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from market.models import Store, StoreAddress, Category, Product
from market.serializers import (
    StoreSerializer, StoreAddressSerializer, CategorySerializer,
    ProductListSerializer, ProductDetailSerializer)
from market.permissions import (
    IsStoreOwner, IsSellerOfAddress, IsSeller, IsSellerOrReadOnly)
from market.services.mixins import AddActivateEndpointMixin


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated(), IsSeller()]
        else:
            return [IsAuthenticated(), IsSeller(), IsStoreOwner()]

    def get_queryset(self):
        # let everyone see the list of stores and details
        if self.action in ['list', 'retrieve']:
            return Store.objects.select_related('seller', 'address').all()
        # only store-owners can modify the store data
        else:
            return Store.objects.filter(seller=self.request.user)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class StoreAddressViewSet(ModelViewSet):
    queryset = StoreAddress.objects.all()
    serializer_class = StoreAddressSerializer
    permission_classes = [IsAuthenticated, IsSellerOfAddress]

    def get_queryset(self):
        return StoreAddress.objects.filter(store__seller=self.request.user)


class CategoryViewSet(ModelViewSet, AddActivateEndpointMixin):
    serializer_class = CategorySerializer
    permission_classes = [IsSellerOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_feilds = ['name', 'id']
    ordering = ['name']

    # modify the queryset method not to return is_active=False to non-admin
    # modify the cache to update when an object activated
    # make it reusable
    def get_queryset(self):
        cached_queryset = cache.get('categories')
        if not cached_queryset:
            queryset = Category.objects.select_related('parent').all()
            cache.set('categories', queryset)
            return queryset
        return cached_queryset

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser]
        )
    def activate(self, requets, pk=None):
        category = self.get_object()
        return self.perform_activate(obj=category)


class ProductViewSet(ModelViewSet, AddActivateEndpointMixin):
    permission_classes = [IsSellerOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ['name', 'id']
    ordering = ['id']

    def get_queryset(self):
        queryset = Product.objects.select_related('category')
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        product = self.get_object()
        return self.perform_activate(obj=product)
