from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.serializers import (
    UserSerializer, PhoneSerializer, OTPLoginSerializer,
    UserAddressSerializer, MiniAddressSerializer)
from account.utils import (
    generate_otp,
    set_otp,
    get_otp,
    delete_otp,
    send_sms_verification_code,
    )

from account.models import UserAddress
from account.permissions import IsAddressOwner

User = get_user_model()


class RegistrationAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class RequestOTPAPIView(APIView):
    # permission_classes = [IsLimitedRequest]

    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        otp = generate_otp()
        set_otp(phone=phone, otp=otp)

        # A quick reach to otp (for test).
        # print(f"OTP {otp} sent to phone {phone}")

        # For production
        send_sms_verification_code(code=otp, phone_number=phone)

        return Response(
            {"message": "The code sent to your phone."},
            status=status.HTTP_200_OK
            )


class OTPLoginAPIView(APIView):
    """Login using otp code sent to user's phone"""
    def post(self, request):
        serializer = OTPLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        user_otp = serializer.validated_data['otp']
        original_otp = get_otp(phone=phone)

        # check if the code is correct
        if (not original_otp) or (user_otp != original_otp):
            return Response(
                {"detail": "Invalid code"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # fetch the user from database
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # delete the otp from redis
        delete_otp(phone)

        # generate the jwt token
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh)
            },
            status=status.HTTP_200_OK
        )


class LogoutAPIView(APIView):

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if refresh_token is None:
            return Response(
                {'detail': 'refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'detail': 'Successfully logged out.'},
                status=status.HTTP_205_RESET_CONTENT
                )
        except TokenError:
            return Response(
                {'detail': 'Invalid token.'},
                status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.prefetch_related('addresses')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @property
    def cache_key(self):
        return f"profile-{self.request.user.id}"

    def retrieve(self, request, *args, **kwargs):

        cached_profile = cache.get(self.cache_key)

        if cached_profile:
            return Response(cached_profile)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(self.cache_key, data, timeout=60*60*24)
        return Response(data)

    def get_object(self):
        return self.queryset.get(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()
        cache.delete(self.cache_key)

    def perform_destroy(self, instance):
        instance.delete()
        cache.delete(self.cache_key)


class UserAddressViewSet(ModelViewSet):
    queryset = UserAddress.objects.select_related('owner').all()
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return UserAddress.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return MiniAddressSerializer
        else:
            return UserAddressSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAddressOwner()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
