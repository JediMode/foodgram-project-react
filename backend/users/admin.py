from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_filter = ('email', 'first_name')
    search_fields = ('username',)
    list_filter = ('username', 'email')
    list_per_page = 10


@admin.register(Follow)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
