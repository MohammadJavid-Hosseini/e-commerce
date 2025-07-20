from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=now())

    def hard_delete(self):
        return super().delete()

    def get_deleted_objects(self):
        return super().filter(is_deleted=True)

    def get_not_deleted_objects(self):
        return super().filter(is_deleted=False)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True


class User(AbstractUser, TimeStampedModel, SoftDeleteModel):

    phone = models.CharField(max_length=16, unique=True, db_index=True)
    is_seller = models.BooleanField(default=False, db_index=True)
    picture = models.ImageField(upload_to="users/", null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['created_at']


class Address(TimeStampedModel, SoftDeleteModel):

    owner = models.ForeignKey(
        to=User, on_delete=models.CASCADE, related_name='addresses',
        default=None, null=True, blank=True)
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
