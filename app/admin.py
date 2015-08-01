from django.contrib import admin
from app.models import *

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Review)
