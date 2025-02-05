from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)