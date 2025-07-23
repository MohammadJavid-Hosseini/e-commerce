from rest_framework.routers import DefaultRouter
from market.views import (StoreViewSet, StoreAddressViewSet)


router = DefaultRouter()
router.register('store', StoreViewSet, basename='store')
router.register('store_address', StoreAddressViewSet, 'store_address')


urlpatterns = router.urls
