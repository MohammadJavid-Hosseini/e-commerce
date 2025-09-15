from django.contrib.auth import get_user_model
from rest_framework import serializers
from market.models import (
    Store, StoreAddress, Category, Image, Product, StoreItem, Cart,
    CartItem, Order, OrderItem, UserAddress, Review, Payment)
from market.services.mixins import RepresentAsStringMixin
from market.services.product_service import get_best_seller_item
from market.tasks import send_order_creation_email

User = get_user_model()


class StoreAddressSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField()

    class Meta:
        model = StoreAddress
        fields = [
            'id', 'store', 'label', 'address_line_1', 'address_line_2',
            'city', 'state', 'country', 'postal_code']
        read_only_fields = ['id', 'store']

    def get_store(self, obj):
        return f'id: {obj.store.id}, name: {obj.store.name}'


class StoreSerializer(serializers.ModelSerializer):
    address = StoreAddressSerializer()
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'description', 'seller', 'address']

    def create(self, validated_data):
        """create store and its address in one action"""
        # pop address and create store with the rest of data
        address = validated_data.pop('address')
        store = Store.objects.create(**validated_data)

        # create store_address
        serializer = StoreAddressSerializer(data=address)
        serializer.is_valid(raise_exception=True)
        created_address = StoreAddress.objects.create(**serializer.validated_data)

        # assign store's address
        store.address = created_address
        store.save()

        return store

    def update(self, instance, validated_data):
        """update store data including store address"""

        # pop address
        address_data = validated_data.pop('address')

        # update the store itself
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # update store address
        if address_data:
            address = instance.address
            for attr, value in address_data.items():
                setattr(address, attr, value)
        address.save()

        return instance


class RecursiveCategorySerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField(method_name='get_parent')

    class Meta:
        model = Category
        fields = ['name', 'parent']

    def get_parent(self, obj):
        if obj.parent:
            return RecursiveCategorySerializer(obj.parent).data
        return None


class CategorySerializer(serializers.ModelSerializer):
    parent = RecursiveCategorySerializer(read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.select_related('parent').all(),
        source='parent',
        write_only=True,
        required=False
        )

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description',
            'image', 'is_active', 'parent', 'parent_id']
        # HACK: later, make is_active read_only as well
        read_only_fields = ['id', 'parent']


class ReviewSerializer(serializers.ModelSerializer,
                       RepresentAsStringMixin):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'user', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate(self, attrs):
        comment = attrs.get('comment')
        rating = attrs.get('rating')

        if comment is None or comment.strip() == '':
            raise serializers.ValidationError("Please leave a comment")
        if not (1 <= rating <= 5):
            raise serializers.ValidationError("rating must be between 1 and 5")
        user = self.context['request'].user
        product = self.context['product']
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                "You have already reviewed this product")

        return attrs

    def get_fields(self):
        fields = super().get_fields()
        return self.to_string(fields, 'user')


class SellerForProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(source='store.name')
    product = serializers.IntegerField(source='product.id')
    price = serializers.CharField()
    discount_price = serializers.CharField(allow_null=True)
    stock = serializers.IntegerField()
    detail_url = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()

    def get_detail_url(self, obj):
        return f"/stores/{obj.store.id}/"

    def get_store(self, obj):
        return {
            'id': obj.store.id,
            'name': obj.store.name,
            'seller': obj.store.seller.username,
            'description': obj.store.description
        }


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'product', 'image']


class ProductDetailSerializer(serializers.ModelSerializer):
    category = RecursiveCategorySerializer(read_only=True)
    reviews = ReviewSerializer(many=True, required=False, read_only=True)
    sellers = serializers.SerializerMethodField()
    best_seller = serializers.SerializerMethodField()
    images = ImageSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'images', 'is_active',
            'rating', 'best_seller', 'best_price', 'reviews', 'sellers'
        ]
        read_only_fields = [
            'images', 'is_active', 'rating', 'best_seller', 'best_price', 'reviews', 'sellers'
        ]

    def get_sellers(self, obj):
        active_items = obj.items.filter(is_active=True).select_related('store', 'product', 'store__seller')
        return SellerForProductSerializer(active_items, many=True).data

    def get_best_seller(self, obj):
        best_item = get_best_seller_item(obj)
        if not best_item:
            return None
        return SellerForProductSerializer(best_item).data


class ProductListSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    rating = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    best_price = serializers.SerializerMethodField()
    best_seller = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'images', 'is_active',
                 'best_seller', 'rating', 'stock', 'best_price']
        read_only_fields = ['id', 'best_seller', 'rating', 'stock', 'best_price']

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            avg_rating = sum(review.rating for review in reviews) / reviews.count()
            return f"{avg_rating:.1f}"
        return "0.0"

    def get_stock(self, obj):
        total_stock = sum(item.stock for item in obj.items.filter(is_active=True))
        return str(total_stock)

    def get_best_price(self, obj):
        active_items = obj.items.filter(is_active=True)
        if active_items.exists():
            # final price = price - (discount or 0)
            best = min(
                (float(i.price) - float(i.discount_price or 0) for i in active_items),
                default=None,
            )
            return best
        return None

    def get_best_seller(self, obj):
        best_item = get_best_seller_item(obj)
        if not best_item:
            return None
        return SellerForProductSerializer(best_item).data


class StoreItemSerializer(serializers.ModelSerializer, RepresentAsStringMixin):

    def get_fields(self):
        fields = super().get_fields()
        self.to_string(fields, 'store')
        self.to_string(fields, 'product')
        return fields

    class Meta:
        model = StoreItem
        fields = [
            'id', 'store', 'product', 'price',
            'discount_price', 'stock', 'is_active']
    # HACK:
    # read_only_fields = ['is_active']


class CartItemSerializer(serializers.ModelSerializer,
                         RepresentAsStringMixin):

    unit_price = serializers.SerializerMethodField()
    unit_discount = serializers.SerializerMethodField()
    final_item_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'store_item', 'quantity',
            'unit_price', 'unit_discount', 'final_item_price',
            'total_price', 'total_discount', 'final_price']
        read_only_fields = [
            'id', 'cart', 'unit_price', 'unit_discount',
            'final_item_price', 'total_price',
            'total_discount', 'final_price']

    def get_unit_price(self, obj):
        return obj.unit_price

    def get_unit_discount(self, obj):
        return obj.unit_discount

    def get_final_item_price(self, obj):
        return obj.final_item_price

    def get_total_price(self, obj):
        return obj.total_price

    def get_total_discount(self, obj):
        return obj.total_discount

    def get_final_price(self, obj):
        return obj.final_price

    def get_fields(self):
        fields = super().get_fields()
        self.to_string(fields, 'cart')
        self.to_string(fields, 'store_item')
        return fields

    def update(self, instance, validated_data):
        quantity = validated_data.get('quantity')
        if quantity <= 0:
            raise serializers.ValidationError("Quantity must not be 0")
        instance.quantity = quantity
        instance.save()

        return instance
    # OPTIMIZE: when creating a cart item, if quantity is not passed set it 1


class MiniCartItemSerializer (serializers.ModelSerializer,
                              RepresentAsStringMixin):

    final_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'store_item', 'quantity', 'final_price']
        read_only_fields = ['id', 'cart', 'final_price']

    def get_final_price(self, obj):
        return obj.final_price

    def get_fields(self):
        fields = super().get_fields()
        return self.to_string(fields, 'store_item')


class CartSerializer(serializers.ModelSerializer, RepresentAsStringMixin):
    items = MiniCartItemSerializer(many=True, required=False)
    total_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'items', 'total_price',
                  'total_discount', 'final_price']
        read_only_fields = ['id', 'customer']

    def get_total_price(self, obj):
        return obj.total_price

    def get_total_discount(self, obj):
        return obj.total_discount

    def get_final_price(self, obj):
        return obj.final_price

    def create(self, validated_data):
        request = self.context.get('request')
        items_data = validated_data.pop('items', [])

        customer = validated_data.get('customer')
        if request and not customer:
            validated_data['customer'] = request.user

        cart, created = Cart.objects.get_or_create(**validated_data)

        if not created:
            cart.items.all().delete()

        for item in items_data:
            if item.get('quantity') <= 0:
                raise serializers.ValidationError("Quantity can not be 0")
            CartItem.objects.create(cart=cart, **item)

        return cart

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])

        # updating cart attrs (other than items)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # update cart's items
        if items_data:
            for item_data in items_data:
                store_item = item_data.get('store_item')
                quantity = item_data.get('quantity')
                if quantity <= 0:
                    raise serializers.ValidationError("Quantity can not be 0")

                # check if cart_item is already added
                cart_item = instance.items.filter(store_item=store_item).first()
                if cart_item:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    CartItem.objects.create(cart=instance, **item_data)

        return instance

    def get_fields(self):
        fields = super().get_fields()
        return self.to_string(fields, 'customer')


class OrderItemSerializer(serializers.ModelSerializer, RepresentAsStringMixin):
    class Meta:
        model = OrderItem
        fields = ['id', 'store_item', 'quantity']
        read_only_fields = ['id']

    def get_fields(self):
        fields = super().get_fields()
        return self.to_string(fields, 'store_item')


class OrderSerializer(serializers.ModelSerializer, RepresentAsStringMixin):

    items = OrderItemSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'address', 'items', 'status', 'total_price', 'created_at']
        read_only_fields = ['id', 'customer', 'items', 'status', 'total_price', 'created_at']

    def create(self, validated_data):
        """create an order using user's cart and then empty the cart"""

        # fetch customer and address
        user = self.context.get('request').user
        address = validated_data.get('address', None)

        # addrss error
        if address is None:
            raise serializers.ValidationError(
                "Address is needed, set one if you haven't yet.")
        address_qs = UserAddress.objects.select_related('owner') \
            .filter(owner=user.id)
        if address not in address_qs.all():
            raise serializers.ValidationError(
                "This address doesn't belog to this user")

        # cart error
        cart = Cart.objects.filter(customer=user).first()
        cart_items = cart.items.all()
        if len(cart_items) == 0:
            raise serializers.ValidationError("Your cart is empty!")

        # create the order
        order = Order.objects.create(customer=user, address=address)
        order_total_price = 0

        # create order-items
        for cart_item in cart_items:
            # check if quantity is available
            quantity = cart_item.quantity
            if quantity > cart_item.store_item.stock:
                raise serializers.ValidationError(
                    f"Only {cart_item.store_item.stock} \
                        items available for '{cart_item.store_item.name}'"
                    )

            unit_price = cart_item.store_item.price
            unit_discount = cart_item.store_item.discount_price or 0
            total_price = unit_price * quantity
            total_discount = unit_discount * quantity
            final_price = total_price - total_discount

            order_total_price += final_price

            OrderItem.objects.create(
                order=order,
                store_item=cart_item.store_item,
                quantity=quantity,
                price=unit_price,
                discount_price=unit_discount,
                total_price=total_price,
                total_discount=total_discount,
                final_price=final_price,
            )

        # add total price to order
        order.total_price = order_total_price
        order.save()

        # empty the cart
        cart.items.all().delete()

        send_order_creation_email.delay(user.email, order.id)

        return order

    def get_fields(self):
        fields = super().get_fields()
        self.to_string(fields, 'customer')
        self.to_string(fields, 'address')
        return fields


class PaymentVerifySerializer(serializers.Serializer):
    merchant_id = serializers.CharField()
    amount = serializers.IntegerField()
    authority = serializers.CharField()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'status',
            'reference_id', 'transaction_id', 'fee', 'card_pan']
        read_only_fields = ['id', 'order', 'amount', 'reference_id']


# class SellerSerializer(serializers.ModelSerializer):
#     name = serializers.CharField(source='username')
#     store = StoreSerializer(many=True, read_only=True)
#     product = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ['id', 'name', 'stores', 'product']

#     def get_product(self, obj):
#         return obj.store.store_item.product
