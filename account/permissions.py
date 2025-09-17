from rest_framework.permissions import BasePermission
from account.utils import redis_client


class IsAddressOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner


class IsLimitedRequest(BasePermission):
    MAX_HIT = 4

    def has_permission(self, request, view):
        phone = request.data.get('phone', None)
        current_count = redis_client.get(name=f"{phone}-count")
        if current_count is None:
            current_count = 0
        current_count = int(current_count) + 1
        redis_client.setex(
            name=f"{phone}-count",
            time=10*60,
            value=current_count
            )
        return current_count > self.MAX_HIT
