from rest_framework.permissions import BasePermission, SAFE_METHODS
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


class IsSellerOrReadOnly(BasePermission):
    """Only sellers access not-saved methods"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_seller


class IsAdminOrReadOnly(BasePermission):
    # an alternative to using IsAdminUser and overriding get_permissions
    # delete the comment later

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff


class IsAdminOrCreateOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return request.user.is_staff
        return request.user.is_authenticated


class IsCartOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return True if request.user.is_staff \
            else request.user == obj.cart.customer
