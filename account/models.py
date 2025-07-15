from django.db import models
from django.contrib.auth.models import AbstractUser


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Address(TimeStampedModel):
    label = models.CharField(max_length=255)
    address_line_1 = models.TextField(max_length=500)
    address_line_2 = models.TextField(max_length=500)
    city = models.CharField(max_length=255, db_index=True)
    state = models.CharField(max_length=255, db_index=True)
    postal_code = models.CharField(max_length=11, db_index=True)
    country = models.CharField(max_length=255, db_index=True)

    def __str__(self):
        return f"{self.label}, {self.address_line_1[:30]}"

    class Meta:
        indexes = [
            models.Index(fields=['city', 'state', 'country'])
        ]


class User(AbstractUser):
    phone = models.CharField(max_length=16, unique=True, db_index=True)
    address = models.ForeignKey(
        to=Address, on_delete=models.SET_NULL, null=True, blank=True)
    is_seller = models.BooleanField(default=False, db_index=True)
    picture = models.ImageField(upload_to="users/", null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['registered_at']
