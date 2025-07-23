from rest_framework.permissions import BasePermission
from market.models import StoreAddress


class IsStoreOwner(BasePermission):
    """Ensure that the user is the owner of the store"""
    def has_object_permission(self, request, view, obj):
        return obj.seller == request.user


class IsSellerOfAddress(BasePermission):
    """
    Ensure only seller of the store can modify the store's address
    """
    def has_object_permission(self, request, view, obj: StoreAddress):
        return hasattr(obj, 'store') and obj.store.seller == request.user


class IsSeller(BasePermission):
    """Check if the user is seller"""
    def has_permission(self, request, view):
        return request.user.is_seller is True
