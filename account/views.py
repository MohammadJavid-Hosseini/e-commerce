from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from account.serializers import UserSerializer, PhoneSerializer
from account.utils import generate_otp, set_otp


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

        # This must be replaced with an SMS service later
        print(f"OTP {otp} sent to phone {phone}")

        return Response(
            {"message": "The code sent to your phone."},
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
