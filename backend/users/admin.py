from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_filter = ('email', 'first_name')


@admin.register(Follow)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
