from django.urls import path
from rest_framework.routers import DefaultRouter
from market.views import (
    StoreViewSet,
    StoreAddressViewSet,
    CategoryViewSet,
    ProductViewSet,
    StoreItemViewSet,
    DashboardViewSet,
    CartViewSet,
    CartItemViewSet,
    OrderViewSet,
    ReviewDetailAPIView,
    PaymentCallbackAPIView,
    OrderItemConfirmationView,
    OrderItemRejectionView,
)

router = DefaultRouter()
router.register('store', StoreViewSet, 'store')
router.register('store_address', StoreAddressViewSet, 'store_address')
router.register('category', CategoryViewSet, 'category')
router.register('product', ProductViewSet, 'product')
router.register('store_item', StoreItemViewSet, 'store_item')
router.register('cart', CartViewSet, 'cart')
router.register('cart_item', CartItemViewSet, 'cart_item')
router.register('order', OrderViewSet, 'order')
router.register('dashboard', DashboardViewSet, 'dashboard')

urlpatterns = [
    path('confirm_item/<int:pk>/', OrderItemConfirmationView.as_view(), name='item-confirm'),
    path('reject_item/<int:pk>/', OrderItemRejectionView.as_view(), name='item-rejection'),
    path('reviews/<int:pk>/', ReviewDetailAPIView.as_view(), name='reviews'),
    path('payment/verify/', PaymentCallbackAPIView.as_view(),
         name='payment-verify')
]


urlpatterns += router.urls
