from django.contrib import admin
from django.contrib.auth import get_user_model
from account.models import UserAddress

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'phone', 'is_seller',
        'created_at', 'last_login', 'picture']
    search_fields = ['username', 'phone', 'email']
    list_filter = ['is_seller']


@admin.register(UserAddress)
class UserAddress(admin.ModelAdmin):
    list_display = ['label', 'country', 'state', 'city']
    search_fields = ['label', 'country', 'state', 'city']
