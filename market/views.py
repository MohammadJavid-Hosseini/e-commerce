import requests
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from market.models import (
    Store,
    StoreAddress,
    Category,
    Product,
    StoreItem,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review,
    Payment,
    ORDERITEM_STATUS_PENDING,
    ORDERITEM_STATUS_REJECTED,
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_PENDING,
    ORDER_STATUS_PROCESSING,
    ORDER_STATUS_FAILED,
    PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_SUCCESS
    )
from market.serializers import (
    StoreSerializer,
    StoreAddressSerializer,
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    StoreItemSerializer,
    CartSerializer,
    CartItemSerializer,
    MiniCartItemSerializer,
    OrderSerializer,
    ReviewSerializer,
    )
from market.permissions import (
    IsStoreOwner,
    IsSellerOfAddress,
    IsSeller,
    IsSellerOrReadOnly,
    IsCartOwner,
    IsOrderOwner,
    IsReviewOwner,
)
from market.services.mixins import (
    AddActivateEndpointMixin,
    CachableQuerySetMixin
)
from market.services.payment_service import PaymentService
from market.services.order_item_actions import (
    confirm_order_items,
    reject_order_items
)
from market.services.dashboard_services import (
    order_items_data,
    seller_rates_data,
)
from market.utlis import SmallPaginatioinSettings, LargePaginatioinSettings
from market.filters import (
    ProductFilter, CategoryFilter, StoreFilter, StoreItemFilter)
from market.tasks import send_order_confirmation_email
from market.custom_exceptions import (
    PaymentNotFoundError,
    PaymentVerificationError
)


class StoreViewSet(ModelViewSet):
    serializer_class = StoreSerializer
    pagination_class = SmallPaginatioinSettings
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    filterset_class = StoreFilter
    search_fields = ['name', 'seller__username']
    ordering_fields = ['id', 'name']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsSeller()] if self.action == 'create' else [IsStoreOwner()]

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
    # FIXME: no need to a viewset for storeaddress
    queryset = StoreAddress.objects.all()
    serializer_class = StoreAddressSerializer
    permission_classes = [IsSellerOfAddress]
    pagination_class = SmallPaginatioinSettings
    filter_backends = [SearchFilter]
    search_fields = ['label', 'city', 'state', 'country']

    def get_queryset(self):
        base_qs = StoreAddress.objects.all()
        return base_qs if self.request.user.is_staff else base_qs.filter(store__seller=self.request.user)


class CategoryViewSet (ModelViewSet,
                       AddActivateEndpointMixin,
                       CachableQuerySetMixin):

    serializer_class = CategorySerializer
    permission_classes = [IsSellerOrReadOnly]
    filter_backends = [OrderingFilter, DjangoFilterBackend, SearchFilter]
    ordering_fields = ['name', 'id']
    ordering = ['name']
    search_fields = ['name']
    filterset_class = CategoryFilter
    pagination_class = SmallPaginatioinSettings

    def get_queryset(self):
        """cache and return the queryset, and limit non-admin access"""

        user = self.request.user
        base_qs = Category.objects.select_related('parent')

        if user.is_staff:
            return self.get_cached_queryset('categories', base_qs.all())

        return self.get_cached_queryset(
            'active_categories',
            base_qs.filter(is_active=True))

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAdminUser]
        )
    def activate(self, request, pk=None):
        """turn is_active attribute into True using custom action"""

        category = self.get_object()
        response = self.perform_activate(obj=category)

        self.clean_cached_qs('categories', 'active_categories')

        return response


class ProductViewSet(ModelViewSet,
                     AddActivateEndpointMixin,
                     CachableQuerySetMixin):

    permission_classes = [IsSellerOrReadOnly]
    filter_backends = [OrderingFilter, DjangoFilterBackend, SearchFilter]
    ordering_fields = ['name', 'id']
    ordering = ['id']
    search_fields = ['name', 'category__name']
    filterset_class = ProductFilter

    pagination_class = LargePaginatioinSettings

    def get_queryset(self):
        qs = Product.objects.select_related('category') \
            .prefetch_related('reviews')
        if self.request.user.is_staff:
            return self.get_cached_queryset('products', qs.all())
        return self.get_cached_queryset(
            'active_products',
            qs.filter(is_active=True)
            )

    def get_serializer_class(self):
        """use a minimal serializer for list"""

        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        """turn is_active attribute into True using custom action"""

        product = self.get_object()
        response = self.perform_activate(obj=product)

        self.clean_cached_qs('products', 'active_products')

        return response

    @action(
        detail=True,
        methods=['get', 'post'],
        permission_classes=[IsAuthenticated]
        )
    def reviews(self, request, pk=None):
        product = self.get_object()

        if request.method == 'GET':
            reviews = Review.objects.filter(product=product)
            serializer = ReviewSerializer(
                # NOTE: request must be passed,
                #       it's needed for serializer's to_string method
                instance=reviews, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'POST':
            serializer = ReviewSerializer(
                data=request.data,
                context={'request': request, 'product': product}
                )

            serializer.is_valid(raise_exception=True)

            Review.objects.create(
                user=request.user, product=product, **serializer.validated_data
            )
            return Response(
                {'detail': 'review added.'}, status=status.HTTP_201_CREATED)


class StoreItemViewSet(ModelViewSet,
                       AddActivateEndpointMixin,
                       CachableQuerySetMixin):

    serializer_class = StoreItemSerializer
    permission_classes = [IsSeller]
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    ordering_fields = ['product', 'price', 'discount_price', 'stock']
    ordering = ['-price']
    filterset_class = StoreItemFilter
    search_fields = ['store__name', 'product__name', 'store__seller__username']
    pagination_class = LargePaginatioinSettings

    def get_queryset(self):
        qs = StoreItem.objects.select_related('store', 'product')
        user = self.request.user
        if user.is_staff:
            return self.get_cached_queryset('all_items', qs.all())
        return self.get_cached_queryset(
            'this_store_items',
            qs.filter(store__seller=user)
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def activate(self, request, pk=None):
        store_item = self.get_object()
        response = self.perform_activate(store_item)

        self.clean_cached_qs('all_items', 'this_store_items')

        return response


class CartViewSet(ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()

    def get_queryset(self):
        if self.request.user.is_staff:
            return Cart.objects.select_related('customer').all()
        Cart.objects.get_or_create(customer=self.request.user)
        return Cart.objects.filter(customer=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({
                'detail': 'Cart deletion is desabled. Use /cart/<id>/empty instead'
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def empty(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        serializer = self.get_serializer(cart)

        return Response(
            {
                "message": "Your cart currently has no Items",
                "cart": serializer.data},
            status=status.HTTP_200_OK
        )

# TODO: implement a celery task to hard_delete soft-deleted cart-items
#       periodically


class CartItemViewSet(ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsCartOwner]

    def get_queryset(self):
        base_qs = CartItem.objects.select_related('cart', 'store_item')
        user = self.request.user
        if user.is_staff:
            return base_qs.all()
        return base_qs.filter(cart__customer=user)

    def get_serializer_class(self):
        if self.action in ['list', 'create']:
            return MiniCartItemSerializer
        return CartItemSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = Cart.objects.filter(customer=self.request.user).first()
        store_item = serializer.validated_data.get('store_item')
        if cart.items.filter(store_item__id=store_item.id).exists():
            return Response(
                {"detail": "The item is already in the cart; just update it."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.validated_data.get('quantity') <= 0:
            return Response(
                {"detail": "Quantity can not be 0"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save(cart=cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # FIXME: check the product availibility (stock) in creating cart item.
        #       although checked when order creation, it is needed here, too.
        # OPTIMIZE: move the create logic to serializer if no good reason here.


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOrderOwner]
    # TODO: set the ordering. for list, updated_at is the key

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.prefetch_related('items').select_related('customer')
        return qs.all() if user.is_staff else qs.filter(customer=user)

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Use order/<int:pk>/cancel/; not Delete method'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED)
    # FIXME: if the order: cancelled, delivered, failed it's OK to delete.

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if not order.is_editable:
            return Response(
                {'detail': f'can not cancel the order; it is {order.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = ORDER_STATUS_CANCELLED
        order.save()
        return Response(
            {'detail': 'Your order cancelled'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def confirm(self, request, pk=None):
        """confirm order if stock is available and reserve the stock"""

        order = self.get_object()
        # check duplication
        if order.status == ORDER_STATUS_PROCESSING:
            return Response(
                {'detail': 'It is already confirmed.'},
                status=status.HTTP_409_CONFLICT
                )

        # check status; pending
        if order.status != ORDER_STATUS_PENDING:
            return Response(
                {'detail': f'Can not confirm; it is {order.status}'},
                status=status.HTTP_409_CONFLICT
                )

        # check itmes' status
        rejected_list = [
            item.id for item in order.items.all()
            if item.status == ORDERITEM_STATUS_REJECTED]
        pending_list = [
            item.id for item in order.items.all()
            if item.status == ORDERITEM_STATUS_PENDING]

        if len(rejected_list) > 0:
            order.status = ORDER_STATUS_FAILED
            order.save()

            return Response(
                {'detail': f'order failed; item rejections: {rejected_list}'},
                status=status.HTTP_409_CONFLICT
            )

        if len(pending_list) > 0:
            return Response(
                {'detail': f'{pending_list} still pending'},
                status=status.HTTP_425_TOO_EARLY
            )

        order.status = ORDER_STATUS_PROCESSING
        order.save()
        user_email = order.customer.email
        order_id = order.id
        send_order_confirmation_email.delay(user_email, order_id)

        return Response(
            {'detail': 'It is confirmed'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        order = self.get_object()
        if not order.is_editable:
            return Response(
                {'detail': 'Cannot update the order status to failed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = ORDER_STATUS_FAILED
        order.save()
        return Response(
            {'detail': 'The order rejected'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsOrderOwner])
    def pay(self, request, pk=None):
        order = self.get_object()

        if order.status != ORDER_STATUS_PROCESSING:
            return Response(
                {'detail': f"Order status must be processing; but it's {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.filter(order=order).first()
        if payment and payment.status == PAYMENT_STATUS_SUCCESS:
            return Response(
                # either sucess or failed
                {'detail': f"It can not paid. it is already been {payment.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if payment and payment.status == PAYMENT_STATUS_PENDING:
            payment.delete()

        # sending data to payment gateway
        payload = {
            'merchant_id': settings.MERCHANT_ID,
            'amount': int(order.total_price),
            'currency': settings.CURRENCY,
            'callback_url': settings.CALLBACK_URL,
            'description': settings.DESCRIPTION,
            'mobile': request.user.phone,
            'email': request.user.email or None,
            'order_id': str(order.id)
        }
        try:
            r = requests.post(
                settings.PAYMENT_REQUEST_GATEWAY,
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-type": "application/json"},
                timeout=10
            )
        except Exception as e:
            return Response(
                {'detail': f'connection error: {e}'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # check the connection response
        result = r.json()
        if result.get('data', {}).get('code') != 100:
            return Response(
                {
                    'detail': 'payment request failed',
                    'errors': f'{result.get('errors')}'
                },
                status=status.HTTP_417_EXPECTATION_FAILED
            )

        # creating Payment object
        authority = result.get('data', {}).get('authority')
        Payment.objects.create(
            order=order,
            status=PAYMENT_STATUS_PENDING,
            reference_id=authority,
            amount=order.total_price
        )

        # redirecting customer to paying url
        pay_url = f'{settings.PAYMENT_GATEWAY}{authority}'
        return Response(
            {'redirect_url': pay_url},
            status=status.HTTP_201_CREATED
        )


class PaymentCallbackAPIView(APIView):
    """
    This is the callback_url for payment gateway;
    It parses the query_params in url,
    calls methods that verify the payment and update the payment in db,
    returns the appropriate response to the user.
    """
    permission_classes = [AllowAny]

    def get(self, request):

        # check query params
        status_param = request.query_params.get('Status')
        authority = request.query_params.get('Authority')

        if status_param != 'OK':
            return Response(
                {'detail': 'Payment was not successful'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # call the payment service for verifying and updating the payment
        try:
            PaymentService.verify_payment(authority)
        except PaymentNotFoundError:
            return Response(
                {'detail': 'The payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except PaymentVerificationError as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_417_EXPECTATION_FAILED
            )

        return Response(
            {'detail': 'You have successfully paid the bill'},
            status=status.HTTP_200_OK
        )


class ReviewDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related('user', 'product').all()
    permission_classes = [IsReviewOwner]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class DashboardViewSet(ViewSet):
    """A controlling manager for all seller stuff"""
    permission_classes = [IsSeller]

    @action(detail=False, methods=['get'])
    def review(self, request):
        """shows all seller's counts and rates"""

        # fetch seller and their stores
        user = request.user
        store_qs = Store.objects.filter(seller=user)
        stores = [store for store in store_qs.all()]

        # fetch statistics for seller and their stores
        seller_rates = seller_rates_data(user, stores)

        return Response(
            {'Seller': user.username, 'Stores Review': seller_rates},
            status=status.HTTP_200_OK
            )

    @action(detail=False, methods=['get'])
    def order_items(self, request):
        """show status-based categories of order items per store"""

        # fetch stores
        stores = list(Store.objects.filter(seller=request.user).all())

        # fetch order items per store
        order_items = order_items_data(stores, request)

        return Response(
            order_items, status=status.HTTP_200_OK
        )

    def _get_order_items_from_request(self, request):

        # check request's data
        ids = request.data.get('ids', [])
        if not ids or not isinstance(ids, list):
            raise ValidationError("You need to pass a list of ids")

        # find items
        order_items = list(
            OrderItem.objects.filter(id__in=ids).select_related('store_item'))

        for item in order_items:
            self.check_object_permissions(request, item)

        return ids, order_items

    @action(detail=False, methods=['post'])
    def confirm_items(self, request):
        """confirm multiple orderitems in one request"""

        try:
            ids, order_items = self._get_order_items_from_request(request)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        # call confirmation service
        try:
            confirm_order_items(order_items)
        except Exception as e:
            return Response({'detail': str(e)}, status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'confirmed': f'{len(order_items)} order items confirmed',
                'missed': f'{len(set(ids)) - len(order_items)} \
                    ids do not exist'
                },
            status=status.HTTP_200_OK
            )

    @action(detail=False, methods=['post'])
    def reject_items(self, request):
        """reject multiple order items in one request"""

        try:
            ids, order_items = self._get_order_items_from_request(request)
        except ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        # call rejection service
        try:
            reject_order_items(order_items)
        except Exception as e:
            return Response({'detail': str(e)}, status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'Rejected'}, status=status.HTTP_200_OK)
