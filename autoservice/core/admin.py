from django.contrib import admin
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import AdminFileWidget

from autoservice.core import models


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            output.append(u'<a href="%s" target="_blank">%s</a>' % (value.url, thumbnail(value)))
        output.append(super(AdminFileWidget, self).render(name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class ImageWidgetAdmin(admin.ModelAdmin):
    image_fields = []

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name in self.image_fields:
            kwargs.pop("request", None)
            kwargs['widget'] = AdminImageWidget
            return db_field.formfield(**kwargs)
        return super(ImageWidgetAdmin, self).formfield_for_dbfield(db_field, **kwargs)


def redirect_one_object(model, obj):
    response = redirect(f'/{model._meta.app_label}/{model._meta.model_name}/add/')
    if obj:
        response = redirect(f'/{model._meta.app_label}/{model._meta.model_name}/{obj.pk}/change/')
    return response


def thumbnail(obj, size='col-md-2'):
    return mark_safe('<img src="{}" class="img-thumbnail {} p-0">'.format(obj.url, size))


@admin.register(models.Config)
class ConfigAdmin(admin.ModelAdmin):

    exclude = ['deleted_at']
    change_form_template = "admin/button_save.html"

    def add_view(self, request, form_url='', extra_context=None):
        if self.model.objects.first():
            return redirect_one_object(self.model, self.model.objects.first())
        return super().add_view(request, form_url='', extra_context=None)

    def changelist_view(self, request, extra_context=None):
        return redirect_one_object(self.model, self.model.objects.first())


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'state', 'updated_at', 'created_at']
    list_display_links = ['id', 'name']


@admin.register(models.State)
class StateAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'uf', 'updated_at', 'created_at']
    list_display_links = ['id', 'name']


@admin.register(models.Week)
class WeekAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'updated_at', 'created_at']
    list_display_links = ['id', 'name']


@admin.register(models.TypePay)
class TypePayAdmin(admin.ModelAdmin):

    list_display = ['id', 'name', 'order', 'updated_at', 'created_at']
    list_display_links = ['id', 'name']
    list_editable = ['order']


@admin.register(models.Service)
class ServiceAdmin(ImageWidgetAdmin):

    list_display = ['id', 'name', 'get_icon', 'updated_at', 'created_at']
    list_display_links = ['id', 'name']
    image_fields = ['icon']

    def get_icon(self, obj):
        return thumbnail(obj.icon)
    get_icon.short_description = 'Icone'
