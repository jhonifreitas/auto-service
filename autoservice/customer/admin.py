from django.contrib import admin

from autoservice.customer import models
from autoservice.core.admin import ImageWidgetAdmin, thumbnail


class ReviewInline(admin.TabularInline):

    model = models.Review
    can_delete = False
    fk_name = 'to_profile'
    readonly_fields = ['from_profile', 'note', 'text']

    def has_add_permission(self, request):
        return False


class JobDoneInline(admin.TabularInline):

    model = models.JobDone
    can_delete = False
    fields = ['get_image']
    readonly_fields = ['get_image']

    def has_add_permission(self, request):
        return False

    def get_image(self, obj):
        return thumbnail(obj.image)
    get_image.short_description = 'Imagem'


@admin.register(models.Profile)
class ProfileAdmin(ImageWidgetAdmin):

    list_display = ['id', 'user', 'get_photo', 'city', 'types', 'created_at']
    list_display_links = ['id', 'user']
    inlines = [JobDoneInline, ReviewInline]
    image_fields = ['photo']

    def get_photo(self, obj):
        if obj.photo:
            return thumbnail(obj.photo)
        return None
    get_photo.short_description = 'Foto'


@admin.register(models.ProfileService)
class ProfileServiceAdmin(admin.ModelAdmin):

    list_display = ['id', 'profile', 'service', 'type_pay', 'price', 'created_at']
    list_display_links = ['id']
    filter_horizontal = ['week']
