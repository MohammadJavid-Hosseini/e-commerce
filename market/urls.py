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
    UserViewSet,
    MyCartAPIView,
    MyCartItemsAPIView,
    AddToCartAPIView,
)

router = DefaultRouter()
router.register('mystore', StoreViewSet, 'mystore')
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
         name='payment-verify'),
    # My Store endpoints
    path('mystore/address/', StoreAddressListAPI.as_view(), name='mystore_addresses'),
    path('mystore/items/', StoreItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='mystore_items'),
    path('mystore/items/<int:pk>/', StoreItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='mystore_item_detail'),
    path('mystore/orderitems/', DashboardViewSet.as_view({'get': 'orderitems'}), name='mystore_orderitems'),
    path('mystore/orderitems/<int:pk>/', DashboardViewSet.as_view({'get': 'orderitems'}), name='mystore_orderitem_detail'),
    # Cart endpoints (FE expectations)
    path('mycart/', MyCartAPIView.as_view(), name='mycart'),
    path('mycart/items/', MyCartItemsAPIView.as_view(), name='mycart_items'),
    path('mycart/items/<int:pk>/', CartItemViewSet.as_view({'patch': 'partial_update', 'delete': 'destroy'}), name='mycart_item_detail'),
    path('mycart/add_to_cart/<int:store_item_id>/', AddToCartAPIView.as_view(), name='add_to_cart'),
    # Admin API endpoints
    path('admin/categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin_categories'),
    path('admin/categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin_category_detail'),
    path('admin/users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='admin_users'),
    path('admin/users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='admin_user_detail'),
]


urlpatterns += router.urls
