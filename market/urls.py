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
router.register('store', StoreViewSet, 'store')
router.register('category', CategoryViewSet, 'category')
router.register('product', ProductViewSet, 'product')
router.register('store_item', StoreItemViewSet, 'store_item')
router.register('cart', CartViewSet, 'cart')
router.register('cart_item', CartItemViewSet, 'cart_item')
router.register('order', OrderViewSet, 'order')
router.register('dashboard', DashboardViewSet, 'dashboard')
router.register('image', ImageViewSet, 'image')

urlpatterns = [
    path('store_address/', StoreAddressListAPI.as_view(), name='store_addresses'),
    path('reviews/<int:pk>/', ReviewDetailAPIView.as_view(), name='reviews'),
    path('payment/verify/', PaymentCallbackAPIView.as_view(),
         name='payment-verify')
]


urlpatterns += router.urls
