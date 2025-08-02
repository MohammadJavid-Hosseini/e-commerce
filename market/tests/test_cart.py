from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.contrib.auth import get_user_model


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
        """Test create an empty cart for a given user"""
        url = reverse('cart')
        res = self.client.post(url, {"customer": self.user}, format='josn')

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data, {
            "customer": self.user.username,
            "items": [],
            "total_price": 0,
            "total_discount": 0,
            "final_price": 0
            }
        )

    def test_create_a_cart_no_user(self):
        """Test creating a cart when no user is passed"""
        url = reverse('cart')
        res = self.client.post(path=url)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data, {
            "customer": self.user.username,
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