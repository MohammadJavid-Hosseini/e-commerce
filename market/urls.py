from django.urls import path
from rest_framework.routers import DefaultRouter
from market.views import (
    StoreViewSet,
    StoreAddressViewSet,
    CategoryViewSet,
    ProductViewSet,
    StoreItemViewSet,
    SellerDashBoardAPIView,
    CartListAPIView,
    )

router = DefaultRouter()
router.register('store', StoreViewSet, 'store')
router.register('store_address', StoreAddressViewSet, 'store_address')
router.register('category', CategoryViewSet, 'category')
router.register('product', ProductViewSet, 'product')
router.register('store_item', StoreItemViewSet, 'store_item')

urlpatterns = [
    path('dashboard/', SellerDashBoardAPIView.as_view(), name='dashboard'),
    path('cart/', CartListAPIView.as_view(), name='cart')
]


urlpatterns += router.urls
