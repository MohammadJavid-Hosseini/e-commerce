from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from account.models import UserAddress
from market.models import (
    StoreItem, Store, StoreAddress, Product, Category, Order)

User = get_user_model()


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='Bob',
            phone='09221234567',
            password='jpass'
        )
        self.client.force_authenticate(user=self.user)
        self.user_address = UserAddress.objects.create(
            owner=self.user,
            label="home",
            address_line_1="No. 23",
            address_line_2="Bank St.",
            city="Chicago",
            state="Chicago",
            country="U.S",
            postal_code="878239"
        )
        self.seller = User.objects.create_user(
            username='Jack',
            phone='09221234568',
            password='jpass2',
            is_seller=True
        )
        self.store_address = StoreAddress.objects.create(
            label='first branch',
            address_line_1='No. 309',
            address_line_2='Main St.',
            city='city1',
            state='state1',
            postal_code='1234567890',
            country='country1'
        )
        self.store = Store.objects.create(
            name='Best IT store',
            description='Buy every thing related to IT',
            seller=self.seller,
            address=self.store_address
        )
        self.category_1 = Category.objects.create(
            name='Cases',
            description='Cases Description',
            is_active=True,
            parent=None
        )
        self.product = Product.objects.create(
            name='Mini Case A2',
            description="description2",
            is_active=True,
            category=self.category_1
        )
        self.store_item_1 = StoreItem.objects.create(
            product=self.product,
            store=self.store,
            price=6000000,
            discount_price=200000,
            stock=190,
            is_active=True,
        )

    def test_create_empty_cart(self):
        """Test creating an empty cart"""
        url = reverse('cart-list')
        res = self.client.post(path=url, data={}, format='json')
        cart_id = res.data['id']
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.data, {
            "id": cart_id,
            "customer": self.user.id,
            "items": [],
            "total_price": 0,
            "total_discount": 0,
            "final_price": 0
            }
        )

    def test_create_cart_with_items(self):
        """Test creating a cart with items all at once"""

        url = reverse('cart-list')
        payload = {
            "items": [
                {
                    "store_item": self.store_item_1.id,
                    "quantity": 2
                }
            ]
        }

        res = self.client.post(url, payload, format='json')
        cart_id = res.data["id"]
        item_id = res.data['items'][0]['id']
        final_price = res.data['items'][0]['final_price']

        self.assertEqual(res.status_code, 201)
        self.assertEqual(
            res.data,
            {
                "id": cart_id,
                "customer": self.user.id,
                "items": [
                    {
                        "id": item_id,
                        "store_item": self.store_item_1.id,
                        "quantity": 2,
                        "final_price": final_price
                        },
                    ],
                "total_price": 12000000.00,
                "total_discount": 400000,
                "final_price": 11600000.00
            }
        )

    def test_update_quantity_in_cart(self):
        """test updating an existing cart by changing the quantity"""

        # creating a cart
        cart_res = self.client.post(
            reverse('cart-list'),
            {
                "items": [
                    {"store_item": self.store_item_1.id, "quantity": 2}]
            },
            format='json'
        )

        # update the cart
        url = reverse('cart-detail', kwargs={'pk': cart_res.data['id']})
        payload = {
            "items": [
                {
                    "store_item": self.store_item_1.id,
                    "quantity": 1
                }
            ]
        }
        res = self.client.patch(url, payload, format='json')
        cart_id = res.data['id']
        item_id = res.data['items'][0]['id']
        final_price = res.data['items'][0]['final_price']

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res.data,
            {
                "id": cart_id,
                "customer": self.user.id,
                "items": [
                    {
                        "id": item_id,
                        "store_item": self.store_item_1.id,
                        "quantity": 1,
                        "final_price": final_price
                        },
                    ],
                "total_price": 6000000,
                "total_discount": 200000,
                "final_price": 5800000
            })

    def test_empty_the_cart(self):
        # creating a cart
        cart_res = self.client.post(
            reverse('cart-list'),
            {
                "items": [
                    {"store_item": self.store_item_1.id, "quantity": 2}]
            },
            format='json'
        )

        # empty the cart
        url = url = reverse('cart-empty', kwargs={'pk': cart_res.data['id']})
        res = self.client.post(path=url)

        self.assertIn(res.data['message'], 'Your cart currently has no Items')
        self.assertEqual(res.data['cart']['items'], [])

    def test_create_order(self):
        # creating a cart
        self.client.post(
            reverse('cart-list'),
            {
                "items": [
                    {"store_item": self.store_item_1.id, "quantity": 2}]
            },
            format='json'
        )
        # creating an order
        url = reverse('order')
        payload = {
            "address": self.user_address.id
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, 201)
        order_id = res.data['id']
        self.assertTrue(Order.objects.filter(id=order_id).exists())
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.customer, self.user)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)
