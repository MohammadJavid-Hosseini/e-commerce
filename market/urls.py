from django.urls import path
from rest_framework.routers import DefaultRouter
from market.views import (
    StoreViewSet,
    StoreAddressViewSet,
    CategoryViewSet,
    ProductViewSet,
    StoreItemViewSet,
    SellerDashBoardAPIView,
    CartViewSet,
    CartItemViewSet,
    )

router = DefaultRouter()
router.register('store', StoreViewSet, 'store')
router.register('store_address', StoreAddressViewSet, 'store_address')
router.register('category', CategoryViewSet, 'category')
router.register('product', ProductViewSet, 'product')
router.register('store_item', StoreItemViewSet, 'store_item')
router.register('cart', CartViewSet, 'cart')
router.register('cart_item', CartItemViewSet, 'cart_item')

urlpatterns = [
    path('dashboard/', SellerDashBoardAPIView.as_view(), name='dashboard'),
]


urlpatterns += router.urls
