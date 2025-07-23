from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from market.models import Store, StoreAddress
from market.serializers import StoreSerializer, StoreAddressSerializer
from market.permissions import IsStoreOwner, IsSellerOfAddress, IsSeller


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated, IsStoreOwner]

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
