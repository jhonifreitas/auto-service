from auditlog.registry import auditlog
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User

from autoservice.core.utils import Phone
from autoservice.storage import get_storage_path
from autoservice.core.models import AbstractBaseModel, City, Service, Week, TypePay


def get_profile_file_path(instance, filename):
    return get_storage_path(filename, 'profiles')


def get_jobs_done_file_path(instance, filename):
    return get_storage_path(filename, 'jobs_done')


class Profile(AbstractBaseModel):

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
        ordering = ['-rating', 'user']

    COMMON = 'common'
    AUTONOMOUS = 'autonomous'

    TYPES = [
        (COMMON, 'Comum'),
        (AUTONOMOUS, 'Autônomo'),
    ]

    user = models.OneToOneField(User, verbose_name='Usuário', on_delete=models.CASCADE, related_name='profile')
    types = models.CharField(verbose_name='Tipo', max_length=255, choices=TYPES, default=COMMON)
    city = models.ForeignKey(City, verbose_name='Cidade', on_delete=models.CASCADE, related_name='profiles')
    phone = models.CharField(verbose_name='Telefone', max_length=11)
    photo = models.ImageField(verbose_name='Foto', upload_to=get_profile_file_path, null=True, blank=True)
    birthday = models.DateField(verbose_name='Data de Nascimento', null=True, blank=True)
    rating = models.DecimalField(verbose_name='Avaliação', max_digits=2, decimal_places=1, default=0)
    about = models.TextField(verbose_name='Sobre', null=True, blank=True)
    expiration = models.DateField(verbose_name='Expiração', default=datetime.now().date() + timedelta(days=90),
                                  null=True, blank=True)

    @property
    def get_phone_formated(self):
        return Phone(self.phone).format()

    def __str__(self):
        return self.user.get_full_name()


class ProfileService(AbstractBaseModel):

    class Meta:
        verbose_name = 'Serviço do perfil'
        verbose_name_plural = 'Serviços do perfil'

    profile = models.ForeignKey(Profile, verbose_name='Perfil', on_delete=models.CASCADE, related_name='services')
    service = models.ForeignKey(Service, verbose_name='Serviço', on_delete=models.CASCADE,
                                related_name='profile_services')
    week = models.ManyToManyField(Week, verbose_name='Dias da Semana', related_name='services')
    start_hour = models.TimeField(verbose_name='Horário Inicial')
    end_hour = models.TimeField(verbose_name='Horário Final')
    type_pay = models.ForeignKey(TypePay, verbose_name='Tipo de Pagamento', on_delete=models.CASCADE,
                                 related_name='services')
    price = models.DecimalField(verbose_name='Preço', max_digits=12, decimal_places=2, null=True, blank=True)


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


class JobDone(AbstractBaseModel):

    class Meta:
        verbose_name = 'Trabalho realizado'
        verbose_name_plural = 'Trabalhos realizados'
        ordering = ['service', '-created_at']

    profile = models.ForeignKey(Profile, verbose_name='Perfil', on_delete=models.CASCADE, related_name='jobs_done')
    service = models.ForeignKey(Service, verbose_name='Serviço', on_delete=models.CASCADE,
                                related_name='jobs_done')
    image = models.ImageField(verbose_name='Imagem', upload_to=get_jobs_done_file_path)


auditlog.register(Review)
auditlog.register(Profile)
auditlog.register(JobDone)
auditlog.register(ProfileService)
