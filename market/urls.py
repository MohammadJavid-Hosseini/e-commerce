from django.urls import path
from rest_framework.routers import DefaultRouter
from market.views import (
    StoreViewSet,
    StoreAddressListAPI,
    CategoryViewSet,
    ImageViewSet,
    ProductViewSet,
    StoreItemViewSet,
    DashboardViewSet,
    CartViewSet,
    CartItemViewSet,
    OrderViewSet,
    ReviewDetailAPIView,
    PaymentCallbackAPIView,
)

router = DefaultRouter()
# router.register('mystore', StoreViewSet, 'store')
router.register('categories', CategoryViewSet, 'category')
router.register('products', ProductViewSet, 'product')
router.register('store_items', StoreItemViewSet, 'store_item')
router.register('carts', CartViewSet, 'cart')
router.register('cart_items', CartItemViewSet, 'cart_item')
router.register('orders', OrderViewSet, 'order')
# router.register('mystore', DashboardViewSet, 'dashboard')
router.register('images', ImageViewSet, 'image')

urlpatterns = [
    path('store_address/', StoreAddressListAPI.as_view(), name='store_addresses'),
    path('reviews/<int:pk>/', ReviewDetailAPIView.as_view(), name='reviews'),
    path('payment/verify/', PaymentCallbackAPIView.as_view(),
         name='payment-verify')
]


urlpatterns += router.urls
