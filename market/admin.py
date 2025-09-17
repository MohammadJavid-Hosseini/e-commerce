from django.contrib import admin
from market.models import (
    Category, Store, StoreItem, StoreAddress, Product, Review)

admin.site.register(Category)
admin.site.register(StoreAddress)
admin.site.register(Store)
admin.site.register(StoreItem)
admin.site.register(Product)
admin.site.register(Review)
