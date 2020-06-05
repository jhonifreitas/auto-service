from django.contrib import admin
from django.utils.safestring import mark_safe

from gojob.customer import models
from gojob.core.admin import ImageWidgetAdmin, thumbnail


class ReviewInline(admin.TabularInline):

    model = models.Review
    can_delete = False
    fk_name = 'to_profile'
    readonly_fields = ['from_profile', 'note', 'text']

    def has_add_permission(self, request):
        return False


class ProfileCategoryInline(admin.TabularInline):

    model = models.ProfileCategory
    can_delete = False
    readonly_fields = ['category', 'type_pay', 'price']

    def has_add_permission(self, request):
        return False


class ServiceProfessionalInline(admin.TabularInline):

    model = models.ServiceProfessional
    can_delete = False
    readonly_fields = ['professional', 'status', 'observation']

    def has_add_permission(self, request):
        return False


class PayRequestInline(admin.TabularInline):

    model = models.PayRequest
    can_delete = False
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


class ServiceImageInline(admin.TabularInline):

    model = models.ServiceImage
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

    list_display = ['id', 'user', 'get_photo', 'city', 'types', 'expiration', 'created_at']
    list_display_links = ['id', 'user']
    inlines = [ProfileCategoryInline, PayRequestInline, GalleryInline, ReviewInline]
    image_fields = ['photo']

    def get_photo(self, obj):
        if obj.photo:
            return thumbnail(obj.photo)
        return None
    get_photo.short_description = 'Foto'


@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = ['id', 'category', 'professional', 'client', 'date', 'time', 'status', 'created_at']
    list_display_links = ['id', 'category']
    inlines = [ServiceProfessionalInline, ServiceImageInline]
