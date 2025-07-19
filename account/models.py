from django.db import models
from django.contrib.auth.models import AbstractUser


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class User(AbstractUser, TimeStampedModel):
    phone = models.CharField(max_length=16, unique=True, db_index=True)
    is_seller = models.BooleanField(default=False, db_index=True)
    picture = models.ImageField(upload_to="users/", null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['registered_at']


class Address(TimeStampedModel):
    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='addresses')
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
