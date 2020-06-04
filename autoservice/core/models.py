from uuid import uuid4

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

from django.db import models
from django.utils.translation import ugettext_lazy as _

from autoservice.core import manager
from autoservice.storage import get_storage_path


def get_category_file_path(instance, filename):
    return get_storage_path(filename, 'categories')


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


class Config(AbstractBaseModel):

    class Meta:
        verbose_name = 'Geral'
        verbose_name_plural = 'Geral'

    trial_period = models.PositiveSmallIntegerField(verbose_name='Dias de avaliação')
    value = models.DecimalField(verbose_name='Valor mensal', max_digits=6, decimal_places=2)
    plan_code = models.CharField(verbose_name='Código do plano', max_length=255)
    plan_name = models.CharField(verbose_name='Nome do plano', max_length=255)
    plan_description = models.TextField(verbose_name='Descrição do plano')


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


class Category(AbstractBaseModel):

    class Meta:
        verbose_name = 'Categoria'
        ordering = ['name']

    name = models.CharField(verbose_name='Nome', max_length=255)
    image = models.ImageField(verbose_name='Imagem', upload_to=get_category_file_path)
    icon = models.ImageField(verbose_name='Icone', upload_to=get_category_file_path)
    hashtags = models.TextField(verbose_name='Hashtags', null=True, blank=True)


class TypePay(AbstractBaseModel):

    class Meta:
        verbose_name = 'Tipo de pagamento'
        verbose_name_plural = 'Tipos de pagamento'
        ordering = ['order']

    name = models.CharField(verbose_name='Nome', max_length=255)
    order = models.PositiveIntegerField(verbose_name='Ordem', default=0)


auditlog.register(City)
auditlog.register(State)
auditlog.register(TypePay)
auditlog.register(Category)
