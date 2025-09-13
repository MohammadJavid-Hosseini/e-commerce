from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView)
from account import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('myuser/address', views.UserAddressViewSet, 'address')

urlpatterns = [
    path('request-otp/', views.RequestOTPAPIView.as_view(), name='request-otp'),
    path('verify-otp/', views.OTPLoginAPIView.as_view(), name='verify-otp'),
    path('register/', views.RegistrationAPIView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('_jwt_login/', TokenObtainPairView.as_view(), name='jwtlogin'),
    path(
        'myuser/', views.CustomerProfileDetailAPIView.as_view(),
        name='customer-profile')
]


urlpatterns += router.urls
