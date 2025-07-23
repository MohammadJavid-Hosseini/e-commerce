from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
from base.models import (
    TimeStampedModel, SoftDeleteModel, SoftDeleteUserManager,
    BassAddressModel)


class User(AbstractUser, TimeStampedModel, SoftDeleteModel):
    # setting the managers
    objects = SoftDeleteUserManager()
    all_objects = UserManager()

    # other fileds of the model
    phone = models.CharField(max_length=16, unique=True, db_index=True)
    is_seller = models.BooleanField(default=False, db_index=True)
    picture = models.ImageField(upload_to="users/", null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['created_at']


class UserAddress(TimeStampedModel, SoftDeleteModel, BassAddressModel):

    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='addresses',
        default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.label}, {self.address_line_1[:30]}"

    class Meta:
        indexes = [
            models.Index(fields=['city', 'state', 'country'])
        ]
