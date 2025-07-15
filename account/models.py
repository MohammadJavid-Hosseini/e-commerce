from django.db import models
from django.contrib.auth.models import AbstractUser


class Address(models.Model):
    label = models.CharField(max_length=255)
    address_line_1 = models.TextField(max_length=500)
    address_line_2 = models.TextField(max_length=500)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=11)
    country = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label}, {self.address_line_1[:30]}"


class User(AbstractUser):
    phone = models.CharField(max_length=16)
    address = models.ForeignKey(to=Address, on_delete=models.SET_NULL, null=True, blank=True)
    is_seller = models.BooleanField(default=False)
    picture = models.ImageField(upload_to="users/", null=True, blank=True)

    def __str__(self):
        return self.username

