from auditlog.registry import auditlog

from django.db import models
from django.contrib.auth.models import User

from autoservice.core.utils import Phone, CPF
from autoservice.storage import get_storage_path
from autoservice.core.models import AbstractBaseModel, City, Category, TypePay


def get_profile_file_path(instance, filename):
    return get_storage_path(filename, 'profiles')


def get_gallery_file_path(instance, filename):
    return get_storage_path(filename, 'gallery')


class Profile(AbstractBaseModel):

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['-rating', 'user']

    COMMON = 'common'
    PROFESSIONAL = 'professional'

    TYPES = [
        (COMMON, 'Comum'),
        (PROFESSIONAL, 'Profissional'),
    ]

    user = models.OneToOneField(User, verbose_name='Usuário', on_delete=models.CASCADE, related_name='profile')
    types = models.CharField(verbose_name='Tipo', max_length=255, choices=TYPES, default=COMMON)
    phone = models.CharField(verbose_name='Telefone', max_length=11)
    photo = models.ImageField(verbose_name='Foto', upload_to=get_profile_file_path, null=True, blank=True)
    birthday = models.DateField(verbose_name='Data de Nascimento', null=True, blank=True)
    cpf = models.CharField(verbose_name='CPF', max_length=11, null=True, blank=True)

    zipcode = models.CharField(verbose_name='CEP', max_length=8, null=True, blank=True)
    city = models.ForeignKey(City, verbose_name='Cidade', on_delete=models.CASCADE, related_name='profiles')
    address = models.CharField(verbose_name='Endereço', max_length=255, null=True, blank=True)
    number = models.CharField(verbose_name='Número', max_length=255, null=True, blank=True)
    district = models.CharField(verbose_name='Bairro', max_length=255, null=True, blank=True)
    complement = models.TextField(verbose_name='Complemento', null=True, blank=True)

    rating = models.DecimalField(verbose_name='Avaliação', max_digits=2, decimal_places=1, default=0)
    expiration = models.DateField(verbose_name='Expiração', null=True, blank=True)

    @property
    def get_phone_formated(self):
        return Phone(self.phone).format()

    @property
    def get_cpf_formated(self):
        return CPF(self.cpf).format()

    def __str__(self):
        return self.user.get_full_name()


class ProfileCategory(AbstractBaseModel):

    class Meta:
        verbose_name = 'Categoria do perfil'
        verbose_name_plural = 'Categorias do perfil'

    profile = models.ForeignKey(Profile, verbose_name='Perfil', on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(Category, verbose_name='Serviço', on_delete=models.CASCADE,
                                 related_name='profile_categories')
    type_pay = models.ForeignKey(TypePay, verbose_name='Tipo de Pagamento', on_delete=models.CASCADE,
                                 related_name='categories')
    price = models.DecimalField(verbose_name='Preço', max_digits=12, decimal_places=2, null=True, blank=True)


class Service(AbstractBaseModel):

    class Meta:
        verbose_name = 'Serviço'

    DONE = 'done'
    RECUSED = 'recused'
    APPROVED = 'approved'
    REQUESTED = 'requested'

    STATUS = [
        (DONE, 'Realizado'),
        (RECUSED, 'Recusado'),
        (APPROVED, 'Aprovado'),
        (REQUESTED, 'Solicitado')
    ]

    from_profile = models.ForeignKey(Profile, verbose_name='De', on_delete=models.CASCADE, related_name='service_from')
    to_profile = models.ForeignKey(Profile, verbose_name='Para', on_delete=models.CASCADE, related_name='service_to')
    status = models.CharField(verbose_name='Status', choices=STATUS, max_length=255)


class Review(AbstractBaseModel):

    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-created_at']

    from_profile = models.ForeignKey(Profile, verbose_name='De', on_delete=models.CASCADE,
                                     related_name='review_from')
    to_profile = models.ForeignKey(Profile, verbose_name='Para', on_delete=models.CASCADE,
                                   related_name='review_to')
    note = models.DecimalField(verbose_name='Nota', default=0, max_digits=2, decimal_places=1)
    text = models.TextField(verbose_name='Texto', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        media = 0
        reviews = Review.objects.filter(to_profile=self.to_profile)
        notes = reviews.values('note').annotate(models.Sum('note'))
        if notes.exists():
            note_sum = notes.first().get('note__sum')
            media = note_sum / reviews.count()
        self.to_profile.rating = media
        self.to_profile.save()


class Gallery(AbstractBaseModel):

    class Meta:
        verbose_name = 'Galeria'
        verbose_name_plural = 'Trabalhos realizados'
        ordering = ['-created_at']

    profile = models.ForeignKey(Profile, verbose_name='Perfil', on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(verbose_name='Imagem', upload_to=get_gallery_file_path)


class PayRequest(AbstractBaseModel):

    class Meta:
        verbose_name = 'Solicitação'
        verbose_name_plural = 'Solicitações'
        ordering = ['-created_at']

    TICKET = 'ticket'
    CREDIT_CARD = 'credit_card'

    WAITING = '1'
    IN_ANALYSIS = '2'
    PAID = '3'
    DISPONIBLE = '4'
    IN_DISPUTE = '5'
    RETURNED = '6'
    CANCELED = '7'
    DEBITED = '8'
    TEMPORARY_RETENTION = '9'

    PAY_TYPES = [
        (TICKET, 'Boleto'),
        (CREDIT_CARD, 'Cartão de Crédito')
    ]

    STATUS = [
        (WAITING, 'Aguardando pagamento'),
        (IN_ANALYSIS, 'Em análise'),
        (PAID, 'Pago'),
        (DISPONIBLE, 'Disponível'),
        (IN_DISPUTE, 'Em disputa'),
        (RETURNED, 'Devolvido'),
        (CANCELED, 'Cancelado'),
        (DEBITED, 'Debitado'),
        (TEMPORARY_RETENTION, 'Retenção temporária'),
    ]

    profile = models.ForeignKey(Profile, verbose_name='Perfil', on_delete=models.CASCADE, related_name='pay_requests')
    code = models.CharField(verbose_name='Código', max_length=255, unique=True)
    payment_link = models.URLField(verbose_name='Link Pagamento', null=True, blank=True)
    payment_type = models.CharField(verbose_name='Tipo de Pagamento', choices=PAY_TYPES, max_length=255)
    status = models.CharField(verbose_name='Status', max_length=1, choices=STATUS, default=WAITING)


auditlog.register(Review)
auditlog.register(Profile)
auditlog.register(Gallery)
auditlog.register(ProfileCategory)
