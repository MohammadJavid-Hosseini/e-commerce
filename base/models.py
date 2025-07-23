from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import UserManager


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=now())

    def hard_delete(self):
        return super().delete()

    def get_deleted_objects(self):
        return self.filter(is_deleted=True)

    def get_not_deleted_objects(self):
        return self.filter(is_deleted=False)

    def restore(self):
        return self.update(is_deleted=False, deleted_at=None)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteUserManager(UserManager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    # setting managers
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    # fields
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True


class BassAddressModel(models.Model):
    label = models.CharField(max_length=255)
    address_line_1 = models.TextField(max_length=500)
    address_line_2 = models.TextField(max_length=500)
    city = models.CharField(max_length=255, db_index=True)
    state = models.CharField(max_length=255, db_index=True)
    postal_code = models.CharField(max_length=11, db_index=True)
    country = models.CharField(max_length=255, db_index=True)

    class Meta:
        abstract = True
