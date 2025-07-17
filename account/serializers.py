from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'phone',
                  'email', 'picture', 'is_seller', 'address']


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=16)

    def validate_phone(self, value):
        if (not value.isdigit()) or (len(value) < 11):
            raise serializers.ValidationError("Invalid Phone number.")
        return value


class OTPLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=16, required=True)
    otp = serializers.CharField(required=True)
