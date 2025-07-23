from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView)
from account import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('address', views.AddressViewSet, 'address')

urlpatterns = [
    path('get_otp/', views.RequestOTPAPIView.as_view(), name='get_otp'),
    path('register/', views.RegistrationAPIView.as_view(), name='register'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('login/', views.OTPLoginAPIView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('_jwt_login/', TokenObtainPairView.as_view(), name='jwtlogin'),
    path(
        'profile/', views.CustomerProfileDetialAPIView.as_view(),
        name='customer-profile')
]


urlpatterns += router.urls
