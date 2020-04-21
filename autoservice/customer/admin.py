from django.contrib import admin

from autoservice.customer import models
from autoservice.core.admin import thumbnail


class ReviewInline(admin.TabularInline):

    model = models.Review
    extra = 1
    can_delete = False
    readonly_fields = ['from_profile', 'note', 'text']

    def has_add_permission(self, request):
        return False


@admin.register(models.Autonomous)
class AutonomousAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'get_photo', 'city', 'rating', 'created_at']
    list_display_links = ['id', 'user']
    inlines = [ReviewInline]

    def get_photo(self, obj):
        if obj.photo:
            return thumbnail(obj.photo)
        return None
    get_photo.short_description = 'Foto'


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = ['id', 'user', 'get_photo', 'city', 'created_at']
    list_display_links = ['id', 'user']

    def get_photo(self, obj):
        if obj.photo:
            return thumbnail(obj.photo)
        return None
    get_photo.short_description = 'Foto'


@admin.register(models.AutonomousService)
class AutonomousServiceAdmin(admin.ModelAdmin):

    list_display = ['id', 'autonomous', 'service', 'type_pay', 'price', 'created_at']
    list_display_links = ['id']
