from django.core.cache import cache
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from market.models import Store, StoreAddress, Category
from market.serializers import (
    StoreSerializer, StoreAddressSerializer, CategorySerializer)
from market.permissions import (
    IsStoreOwner, IsSellerOfAddress, IsSeller, IsAdminOrReadOnly)


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSellerOfAddress]

    def get_queryset(self):
        return StoreAddress.objects.filter(store__seller=self.request.user)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        cached_queryset = cache.get('categories')
        if not cached_queryset:
            queryset = Category.objects.select_related('parent').all()
            cache.set('categories', queryset)
            return queryset
        return cached_queryset
