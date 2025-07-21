from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


User = get_user_model()


class CustomerTests(APITestCase):
    """Test retrieving and updating customer profiles."""

    def setUp(self):
        self.phone = '09901234567'
        self.user = User.objects.create_user(
            username="userone",
            password="useronepass",
            email="useremail@gmail.com",
            phone=self.phone,
        )
        # skip authentication process
        self.client.force_authenticate(user=self.user)

    def test_retrieve_customer_profile(self):
        url = reverse('customer-profile')
        res = self.client.get(path=url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                'id': self.user.id,
                'username': "userone",
                'email': "useremail@gmail.com",
                'phone': self.phone,
            }
        )

    def test_update_customer_profile(self):
        url = reverse('customer-profile')
        payload = {
            "username": "newusername"
        }

        res = self.client.patch(path=url, data=payload, format='json')
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.username, "newusername")
        # or self.assertEqual(res.data["username"], "newusername")
