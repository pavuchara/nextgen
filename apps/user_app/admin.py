from django.contrib import admin
from .models import NextgenUser


@admin.register(NextgenUser)
class NextgenUserAdmin(admin.ModelAdmin):
    pass
