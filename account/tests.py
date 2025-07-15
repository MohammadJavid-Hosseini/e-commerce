from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from account.utils import generate_test_image

User = get_user_model()

class AuthenticationTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="userone",
            password="useronepass",
            email="useremail@gmail.com",
            phone="09023456789"
        )
        
    def test_registration(self):
        image_file = generate_test_image()
        payload = {
            "username": "newuser",
            "password": "newpass9876",
            "phone": "09123456789",
            "email": "newuser@gmail.com",
            "is_seller": True,
            "picture": image_file, 
        }

        res = self.client.post(
            path=reverse('register'), data=payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_with_phone(self):
        payload = {
            "username": self.user.phone,
            "password": "useronepass"
        }

        res = self.client.post(
            path=reverse('login'), data=payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_logout(self):
        """Test logging out using refresh token blacklisting"""
        
        # Log in to get the refresh token
        payload = {
            "username": self.user.phone,
            "password": "useronepass"
        }
        login_res = self.client.post(reverse('login'), payload, 'json')
        access_token = login_res.data.get('access')
        refresh_token = login_res.data.get('refresh')

        # Send the refresh token to logout endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_res = self.client.post(
            reverse('logout'), data={'refresh': refresh_token}, format='json')

        self.assertEqual(logout_res.status_code, status.HTTP_205_RESET_CONTENT)
        
        # Try to use the same refresh token again (should be blacklisted)
        refresh_res = self.client.post(
            reverse('refresh'), data={'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_res.status_code, status.HTTP_401_UNAUTHORIZED)
