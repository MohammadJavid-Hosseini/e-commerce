from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.serializers import (
    UserSerializer, PhoneSerializer, OTPLoginSerializer)
from account.utils import (
    generate_otp, set_otp, get_otp, delete_otp, send_sms_verification_code)


User = get_user_model()


class RegistrationAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class RequestOTPAPIView(APIView):

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


class CustomerProfileDetialAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        return self.request.user
