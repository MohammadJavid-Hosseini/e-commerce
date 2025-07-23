from rest_framework import serializers
from django.contrib.auth import get_user_model
from account.models import UserAddress


User = get_user_model()


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=16)

    def validate_phone(self, value):
        if (not value.isdigit()) or (len(value) < 11):
            raise serializers.ValidationError("Invalid Phone number.")
        return value


class OTPLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=16, required=True)
    otp = serializers.CharField(required=True)


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            'owner', 'label', 'address_line_1', 'address_line_2',
            'city', 'state', 'country', 'postal_code']

        read_only_fields = ['owner']


class MiniAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = ['label', 'city', 'postal_code']


class UserSerializer(serializers.ModelSerializer):
    addresses = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'phone',
                  'email', 'picture', 'is_seller', 'addresses']
