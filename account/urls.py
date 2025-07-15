from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView)
from account import views


urlpatterns = [
    path('register/', views.RegistrationAPIView.as_view(), name='register'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
]