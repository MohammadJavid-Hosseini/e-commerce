from rest_framework import serializers
from django.contrib.auth import get_user_model
from account.models import Address


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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'owner', 'label', 'address_line_1', 'address_line_2',
            'city', 'state', 'country', 'postal_code']


class MiniAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['label', 'city', 'postal_code']


class UserSerializer(serializers.ModelSerializer):
    addresses = MiniAddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'phone',
                  'email', 'picture', 'is_seller', 'addresses']
