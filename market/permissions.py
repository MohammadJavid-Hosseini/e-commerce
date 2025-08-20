from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
    IsAuthenticated
)
from market.models import StoreAddress


class IsSeller(IsAuthenticated):
    """Check if the user is seller"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_seller


class IsSellerOrReadOnly(IsAuthenticated):
    """Only sellers access non SAFE METHODS"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view) and request.user.is_seller


class IsStoreOwner(IsAuthenticated):
    """Ensure that the user is the owner of the store"""
    def has_object_permission(self, request, view, obj):
        return request.user.is_seller and obj.seller == request.user


class IsSellerOfAddress(IsAuthenticated):
    """
    Ensure only seller of the store can modify the store's address
    """
    def has_object_permission(self, request, view, obj: StoreAddress):
        return hasattr(obj, 'store') and obj.store.seller == request.user


class IsCartOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return True if user.is_staff else request.user == obj.cart.customer


class IsOrderOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.customer == request.user


class IsOrderItemSeller(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return obj.store_item.store.seller == request.user


class IsReviewOwner(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj.user == request.user
