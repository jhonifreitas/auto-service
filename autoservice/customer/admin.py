from django.contrib import admin
from django.utils.safestring import mark_safe

from autoservice.customer import models
from autoservice.core.admin import ImageWidgetAdmin, thumbnail


class ReviewInline(admin.TabularInline):

    model = models.Review
    can_delete = False
    fk_name = 'to_profile'
    readonly_fields = ['from_profile', 'note', 'text']

    def has_add_permission(self, request):
        return False


class PayRequestInline(admin.TabularInline):

    model = models.PayRequest
    # can_delete = False
    fields = ['code', 'get_payment_link', 'payment_type', 'status']
    readonly_fields = ['code', 'get_payment_link', 'payment_type', 'status']

    def has_add_permission(self, request):
        return False

    def get_payment_link(self, obj):
        html = '-'
        if obj.payment_link:
            html = '<a href="{}" target="_blank">Clique aqui</a>'.format(obj.payment_link)
        return mark_safe(html)
    get_payment_link.short_description = 'Link Pagamento'


class GalleryInline(admin.TabularInline):

    model = models.Gallery
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
    inlines = [GalleryInline, ReviewInline, PayRequestInline]
    image_fields = ['photo']

    def get_photo(self, obj):
        if obj.photo:
            return thumbnail(obj.photo)
        return None
    get_photo.short_description = 'Foto'


@admin.register(models.ProfileCategory)
class ProfileCategoryAdmin(admin.ModelAdmin):

    list_display = ['id', 'profile', 'category', 'type_pay', 'price', 'created_at']
    list_display_links = ['id']
