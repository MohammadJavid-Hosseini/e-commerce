from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers
from django.db.models import QuerySet
from django.core.cache import cache


class AddActivateEndpointMixin:

    def perform_activate(self, obj):

        if obj.is_active:
            return Response(
                {'detail': 'It is already activated'},
                status=status.HTTP_400_BAD_REQUEST)

        obj.is_active = True
        obj.save()

        return Response(
            {'detail': 'It is activated'},
            status=status.HTTP_200_OK
        )


class CachableQuerySetMixin:
    def get_cached_queryset(self, key: str, qs: QuerySet, timeout=300):
        cached_qs = cache.get(key)
        if cached_qs:
            return cached_qs
        cache.set(key, qs, timeout=timeout)
        return qs

    def clean_cached_qs(self, *keys):
        for key in keys:
            cache.delete(key)


class RepresentAsStringMixin():
    def to_string(self, fields=None, field_name=None, many=False):
        request = self.context.get('request')
        if request.method == 'GET':
            fields[field_name] = serializers.StringRelatedField(
                many=many, read_only=True)
        return fields
