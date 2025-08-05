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
    OrderCreateListAPIView,
    OrderDetailAPIView,
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
    path('order/', OrderCreateListAPIView.as_view(), name='order'),
    path('order/<int:pk>/', OrderDetailAPIView.as_view(), name='order-detail'),
    # path('order/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel'),
]


urlpatterns += router.urls
