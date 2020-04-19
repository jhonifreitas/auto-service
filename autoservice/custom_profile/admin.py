from django.contrib import admin

from autoservice.custom_profile import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'updated_at', 'created_at']
    list_display_links = ['id', 'user']
