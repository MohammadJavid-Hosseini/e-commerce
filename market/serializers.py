from rest_framework import serializers
from market.models import Store, StoreAddress, Category


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


class CategorySerializer(serializers.ModelSerializer):
    parent = serializers.StringRelatedField(read_only=True)
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
