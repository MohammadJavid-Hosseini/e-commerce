from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from market.models import Store, StoreAddress, Category, Product, StoreItem
from market.serializers import (
    StoreSerializer,
    StoreAddressSerializer,
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    StoreItemSerializer
    )
from market.permissions import (
    IsStoreOwner, IsSellerOfAddress, IsSeller, IsSellerOrReadOnly)
from market.services.mixins import (
    AddActivateEndpointMixin,
    CachableQuerySetMixin
)
from market.utlis import SmallPaginatioinSettings, LargePaginatioinSettings


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    pagination_class = SmallPaginatioinSettings

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
    pagination_class = SmallPaginatioinSettings

    def get_queryset(self):
        return StoreAddress.objects.filter(store__seller=self.request.user)


class CategoryViewSet (ModelViewSet,
                       AddActivateEndpointMixin,
                       CachableQuerySetMixin):

    serializer_class = CategorySerializer
    permission_classes = [IsSellerOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ['name', 'id']
    ordering = ['name']
    pagination_class = SmallPaginatioinSettings

    def get_queryset(self):
        """cache and return the queryset, and limit non-admin access"""

        user = self.request.user
        base_qs = Category.objects.select_related('parent')

        if user.is_staff:
            return self.get_cached_queryset('categories', base_qs.all())

        return self.get_cached_queryset(
            'active_categories',
            base_qs.filter(is_active=True))

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser]
        )
    def activate(self, request, pk=None):
        """turn is_active attribute into True using custom action"""

        category = self.get_object()
        response = self.perform_activate(obj=category)

        self.clean_cached_qs('categories', 'active_categories')

        return response


class ProductViewSet(ModelViewSet,
                     AddActivateEndpointMixin,
                     CachableQuerySetMixin):

    permission_classes = [IsSellerOrReadOnly]
    filter_backends = [OrderingFilter]
    ordering_fields = ['name', 'id']
    ordering = ['id']
    pagination_class = LargePaginatioinSettings

    def get_queryset(self):
        base_qs = Product.objects.select_related('category')
        if self.request.user.is_staff:
            return self.get_cached_queryset('products', base_qs.all())
        return self.get_cached_queryset(
            'active_products',
            base_qs.filter(is_active=True)
            )

    def get_serializer_class(self):
        """use a minimal serializer for list"""

        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """turn is_active attribute into True using custom action"""

        product = self.get_object()
        response = self.perform_activate(obj=product)

        self.clean_cached_qs('products', 'active_products')

        return response


class StoreItemViewSet(ModelViewSet,
                       AddActivateEndpointMixin,
                       CachableQuerySetMixin):

    serializer_class = StoreItemSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    filter_backends = [OrderingFilter]
    ordering_fields = ['product', 'price', 'discount_price', 'stock']
    ordering = ['-price']

    def get_queryset(self):
        qs = StoreItem.objects.select_related('store', 'product')
        user = self.request.user
        if user.is_staff:
            return self.get_cached_queryset('all_items', qs.all())
        return self.get_cached_queryset(
            'this_store_items',
            qs.filter(store__seller=user)
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        store_item = self.get_object()
        response = self.perform_activate(store_item)

        self.clean_cached_qs('all_items', 'this_store_items')

        return response


# class SellerDashBoardAPIView(APIView):
#     """Indicate seller-related stores, categories, and products"""

#     def get(self, request):
#         user = request.user
#         stores = Store.objects.filter(seller=user).count()
#         categories = Category.objects.filter(products__)
