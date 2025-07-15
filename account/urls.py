from django.urls import path
from account import views


urlpatterns = [
    path('register/', views.RegistrationAPIView.as_view(), name='register')
]