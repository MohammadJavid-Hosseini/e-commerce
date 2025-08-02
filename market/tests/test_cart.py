from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


User = get_user_model()


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='javid',
            phone='09221234567',
            password='jpass'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_empty_cart(self):
        """Test creating an empty cart"""
        url = reverse('cart')
        res = self.client.post(path=url, data={}, format='json')

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data, {
            "id": 1,
            "customer": self.user.id,
            "items": [],
            "total_price": 0,
            "total_discount": 0,
            "final_price": 0
            }
        )

    # def test_create_cart_with_items(self):
    #     """Test creating a cart with items all at once"""
    #     url = reverse('cart')
    #     payload = {

    #     }
    #     res = self.client.post
