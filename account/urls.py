from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from account import views


urlpatterns = [
    path('register/', views.RegistrationAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login')
]