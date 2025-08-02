from rest_framework import serializers
from market.models import (
    Store, StoreAddress, Category, Product, StoreItem, Cart, CartItem)
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


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['store_item', 'quantity']


class CartSerializer(serializers.ModelSerializer, RepresentAsStringMixin):
    items = CartItemSerializer(many=True)
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

        cart, success = Cart.objects.get_or_create(**validated_data)

        if not success:
            cart.items.all().delete()

        for item in items_data:
            CartItem.objects.create(cart=cart, **item)

        return cart

    def get_fields(self):
        fields = super().get_fields()
        return self.to_string(fields, 'customer')
