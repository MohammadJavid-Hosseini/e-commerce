from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthenticationTests(TestCase):
    
    def setUp(self):
        self.client = APIClient()

    def test_registration(self):
        payload = {
            "username": "newuser",
            "password": "newpass9876",
            "phone": "09123456789",
            "email": "newuser@gmail.com"
        }

        res = self.client.post(
            path=reverse('register'), data=payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertIn('token', res.data)
        self.assertIn('refresh', res.data)
