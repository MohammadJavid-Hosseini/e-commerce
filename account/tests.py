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

    def test_log_in_with_phone(self):
        payload = {
            "username": self.user.phone,
            "password": "useronepass"
        }

        res = self.client.post(
            path=reverse('login'), data=payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
