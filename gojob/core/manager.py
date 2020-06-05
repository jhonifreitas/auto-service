from django.db import models


class JsonQuerySet(models.query.QuerySet):

    def get_object(self, obj):
        return {
            'pk': obj.pk,
            'name': obj.name
        }

    def get_json(self):
        return [self.get_object(obj) for obj in self]


class JsonManager(models.Manager):

    def get_queryset(self):
        return JsonQuerySet(self.model, using=self._db).all()

    def get_json(self):
        return self.get_queryset().get_json()
