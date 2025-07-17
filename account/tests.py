from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from account.utils import generate_test_image

User = get_user_model()


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.phone = "09023456789"
        self.user = User.objects.create_user(
            username="userone",
            password="useronepass",
            email="useremail@gmail.com",
            phone=self.phone
        )

    def test_registration(self):
        image_file = generate_test_image()
        payload = {
            "username": "newuser",
            "password": "newpass9876",
            "phone": "09123333333",
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
            "username": self.phone,
            "password": "useronepass"
        }

        res = self.client.post(
            path=reverse('jwtlogin'), data=payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_logout(self):
        """Test logging out using refresh token blacklisting"""

        # Log in to get the refresh token
        payload = {
            "username": self.phone,
            "password": "useronepass"
        }
        login_res = self.client.post(
            reverse('jwtlogin'), payload, format='json')
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
        self.assertEqual(
            refresh_res.status_code, status.HTTP_401_UNAUTHORIZED)


class OTPAuthenticationTests(APITestCase):
    def setUp(self):
        self.phone = "09331234567"

    def create_user(self, phone=None, username='user1'):
        return User.objects.create_user(
            username=username,
            password="userpass1",
            email="user1@gmail.com",
            phone=phone
        )

    def login_with_otp(self, otp='123456', phone=None):
        url = reverse('login')
        payload = {"phone": phone or self.phone, "otp": otp}
        return self.client.post(
            path=url, data=payload, format='json'
        )

    @patch("account.views.set_otp")
    def test_request_otp(self, mock_setex):
        url = reverse('request_otp')
        res = self.client.post(
            path=url, data={'phone': self.phone}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        mock_setex.assert_called_once()
        self.assertIn('message', res.data)

    @patch("account.views.get_otp", return_value="123456")
    def test_otp_login_with_redis(self, mock_get):
        self.create_user(phone=self.phone)
        response = self.login_with_otp(phone=self.phone)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    @patch("account.views.get_otp", return_value="123456")
    def test_login_with_wrong_otp(self, mock_get):
        self.create_user(phone=self.phone)
        res = self.login_with_otp(otp='000000', phone=self.phone)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['detail'], 'Invalid code')

    @patch("account.views.get_otp", return_value=None)
    def test_login_with_expired_otp(self, mock_get):
        res = self.login_with_otp(phone=self.phone)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['detail'], 'Invalid code')

    @patch("account.views.get_otp", return_value="123456")
    def test_login_with_unregistered_phone(self, mock_get):
        res = self.login_with_otp(phone="09999999999")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['detail'], 'User not found')

    @patch("account.views.get_otp", return_value="123456")
    def test_otp_logout(self, mock_get):
        """Test logging out using otp login"""
        self.create_user(phone=self.phone)
        # Log in to get the refresh token
        login_res = self.login_with_otp(phone=self.phone)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
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
