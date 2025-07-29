from rest_framework.routers import DefaultRouter
from market.views import (
    StoreViewSet, StoreAddressViewSet, CategoryViewSet, ProductViewSet)


router = DefaultRouter()
router.register('store', StoreViewSet, basename='store')
router.register('store_address', StoreAddressViewSet, 'store_address')
router.register('category', CategoryViewSet, 'category')
router.register('product', ProductViewSet, basename='product')

urlpatterns = router.urls
