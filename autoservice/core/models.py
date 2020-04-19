from uuid import uuid4

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoservice.core import manager
from autoservice.storage import get_storage_path


def get_service_file_path(instance, filename):
    return get_storage_path(filename, 'profiles')


class AbstractBaseModel(models.Model):

    class Meta:
        abstract = True

    history = AuditlogHistoryField()
    uuid = models.UUIDField(verbose_name='UUID', default=uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(verbose_name=_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('Updated at'), auto_now=True)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if hasattr(self, 'title'):
            return self.title
        return str(self.pk)


class State(AbstractBaseModel):

    class Meta:
        verbose_name = 'Estado'

    name = models.CharField(verbose_name='Nome', max_length=255)
    uf = models.CharField(verbose_name='UF', max_length=2)


class City(AbstractBaseModel):

    class Meta:
        verbose_name = 'Cidade'
        ordering = ['name']

    objects = manager.JsonManager()

    state = models.ForeignKey(State, verbose_name='Estado', on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(verbose_name='Nome', max_length=255)


class Service(AbstractBaseModel):

    class Meta:
        verbose_name = 'Serviço'
        ordering = ['name']

    name = models.CharField(verbose_name='Nome', max_length=255)
    icon = models.ImageField(verbose_name='Icone', upload_to=get_service_file_path)


class Week(AbstractBaseModel):

    class Meta:
        verbose_name = 'Dia da Semana'
        verbose_name_plural = 'Dias da Semana'
        ordering = ['name']

    name = models.CharField(verbose_name='Nome', max_length=255)


auditlog.register(City)
auditlog.register(State)
auditlog.register(Service)
