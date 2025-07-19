from django.db import models
from django.contrib.auth import get_user_model
from account.models import Address, TimeStampedModel

User = get_user_model()


# Set the choices
# Rating status
RATING_5 = '5'
RATING_4 = '4'
RATING_3 = '3'
RATING_2 = '2'
RATING_1 = '1'

RATING_CHOICES = [
    (RATING_5, 'Excellent'), (RATING_4, 'Very good'),
    (RATING_3, 'Good'), (RATING_2, 'Not good'), (RATING_1, 'Awful')
]

# Order status
ORDER_STATUS_PENDING = 'pending'
ORDER_STATUS_PROCESSING = 'processing'
ORDER_STATUS_DELIVERED = 'delivered'
ORDER_STATUS_CANCELLED = 'cancelled'
ORDER_STATUS_FAILED = 'failed'

STATUS_CHOICES = [
    (ORDER_STATUS_PENDING, 'Pending'),
    (ORDER_STATUS_PROCESSING, 'Processing'),
    (ORDER_STATUS_DELIVERED, 'Delivered'),
    (ORDER_STATUS_CANCELLED, 'Cancelled'),
    (ORDER_STATUS_FAILED, 'Failed')
]

# Payment status
PAYMENT_STATUS_SUCCESS = 'success'
PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_FAILED = 'failed'

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_STATUS_SUCCESS, 'Success'),
    (PAYMENT_STATUS_PENDING, 'Pending'),
    (PAYMENT_STATUS_FAILED, 'Failed'),
]


class Store(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    seller = models.ForeignKey(
        to=User, on_delete=models.RESTRICT, related_name='stores')
    address = models.OneToOneField(to=Address, on_delete=models.RESTRICT)

    def __str__(self):
        return self.name


class Category(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    parent = models.ForeignKey(
        to='self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subcategories')

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(
        to=Category, on_delete=models.SET_NULL, null=True,
        related_name='products')
    rating = models.CharField(max_length=1, choices=RATING_CHOICES)
    best_seller = models.ForeignKey(
        to=User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='best_selling_products')
    best_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Image(TimeStampedModel):
    image = models.ImageField(upload_to='products/')
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, related_name='images')


class StoreItem(TimeStampedModel):
    store = models.ForeignKey(
        to=Store, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, related_name='items')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('store', 'product')

    def __str__(self):
        return f"{self.product.name} - {self.store.name}"


class Cart(TimeStampedModel):
    customer = models.ForeignKey(
        to=User, on_delete=models.CASCADE)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(
        to=Cart, on_delete=models.CASCADE, related_name='items')
    store_item = models.ForeignKey(to=StoreItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_item_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    # computed fields
    # total_discount = models.DecimalField(max_digits=10, decimal_places=2)
    # total_price = models.DecimalField(max_digits=10, decimal_places=2)


class Order(TimeStampedModel):
    customer = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='orders')
    address = models.ForeignKey(to=Address, on_delete=models.DO_NOTHING)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=ORDER_STATUS_PENDING)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.customer.username} - order {self.id}"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, related_name='items')
    store_item = models.ForeignKey(to=StoreItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)


class Payment(TimeStampedModel):
    order = models.ForeignKey(to=Order, on_delete=models.DO_NOTHING)
    status = models.CharField(
        max_length=15, choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_PENDING)
    transaction_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference_id = models.CharField(max_length=255)
    card_pan = models.CharField(max_length=255)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Review(TimeStampedModel):
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(
        to=Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.CharField(max_length=1, choices=RATING_CHOICES)
    comment = models.TextField()

    def __str__(self):
        return f"{self.user}: {self.comment}"
