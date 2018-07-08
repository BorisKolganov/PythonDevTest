from django.contrib import admin

# Register your models here.
from core.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass