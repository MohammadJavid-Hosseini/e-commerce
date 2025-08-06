from rest_framework import serializers
from market.models import (
    Store, StoreAddress, Category,
    Product, StoreItem, Cart, CartItem, Order, OrderItem)
from market.services.mixins import RepresentAsStringMixin


class StoreAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreAddress
        fields = [
            'id', 'label', 'address_line_1', 'address_line_2',
            'city', 'state', 'country', 'postal_code']


class StoreSerializer(serializers.ModelSerializer):
    address = StoreAddressSerializer(read_only=True)
    # an alternative to overriding get_fields
    # delete the comment later
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=StoreAddress.objects.all(),
        source='address',
        write_only=True,
        required=False
    )
    seller = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'description', 'seller', 'address', 'address_id']


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


class ProductDetailSerializer(serializers.ModelSerializer):
    category = RecursiveCategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'is_active',
            'rating', 'best_seller', 'best_price'
        ]
        read_only_fields = [
            'is_active', 'rating', 'best_seller', 'best_price'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category']

        ordering = ['name']


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

    read_only_fields = ['is_active']


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
            raise serializers.ValidationError("Quantity must not be 0", 400)

    # NOTE: when creating a cart item, if quantity is not passed set it 1


class MiniCartItemSerializer (serializers.ModelSerializer,
                              RepresentAsStringMixin):

    final_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'store_item', 'quantity', 'final_price']
        read_only_fields = ['id', 'final_price']

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
                raise serializers.ValidationError("Quantity can not be 0", 400)
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
                    raise serializers.ValidationError(
                        "Quantity can not be 0", 400)

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
        fields = ['store_item', 'quantity']

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
                "Address is needed, set one if you haven't yet.", 400)

        # cart error
        cart = Cart.objects.filter(customer=user).first()
        cart_items = cart.items.all()
        if len(cart_items) == 0:
            raise serializers.ValidationError("Your cart is empty!", 400)

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

        return order

    def get_fields(self):
        fields = super().get_fields()
        self.to_string(fields, 'customer')
        self.to_string(fields, 'address')
        return fields
