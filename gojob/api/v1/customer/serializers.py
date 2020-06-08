from datetime import datetime

from rest_framework import serializers

from django.contrib.auth.models import User

from gojob.customer import models
from gojob.core.utils import Phone, ZipCode, CPF
from gojob.core.push_notification import PushNotification
from gojob.api.v1.core.serializers import (CitySerializerRetrieve, CategorySerializerRetrieve,
                                           TypePaySerializerRetrieve)


class ProfileSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=15)
    cpf = serializers.CharField(max_length=14, required=False)
    zipcode = serializers.CharField(max_length=9, required=False)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    birthday = serializers.CharField(required=False)
    password = serializers.CharField()

    class Meta:
        model = models.Profile
        fields = ['name', 'email', 'cpf', 'photo', 'city', 'phone', 'birthday', 'lat', 'lng', 'zipcode', 'address',
                  'district', 'number', 'complement', 'password', 'onesignal']

    def validate_phone(self, value):
        return Phone(value).cleaning()

    def validate_cpf(self, value):
        return CPF(value).cleaning()

    def validate_zipcode(self, value):
        return ZipCode(value).cleaning()

    def validate_birthday(self, value):
        return value[:10]

    def validate(self, data):
        email = data.get('email')
        if self.instance and User.objects.filter(username=email).exclude(id=self.instance.user.id).exists():
            raise serializers.ValidationError('Email já cadastrado!', code='invalid')
        return data

    def get_first_name(self, name):
        list_name = name.split(' ')
        return list_name[0]

    def get_last_name(self, name):
        list_name = name.split(' ')
        return ' '.join(list_name[1:])

    def create(self, validated_data):
        name = validated_data.pop('name')
        email = validated_data.pop('email')
        data_user = {
            'first_name': self.get_first_name(name),
            'last_name': self.get_last_name(name),
            'username': email,
            'email': email,
            'password': validated_data.pop('password')
        }
        user = User.objects.create_user(**data_user)
        return self.Meta.model.objects.create(**validated_data, user=user)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        name = validated_data.get('name')
        email = validated_data.get('email')
        if name:
            instance.user.fisrt_name = self.get_first_name(name)
            instance.user.last_name = self.get_last_name(name)
            instance.user.email = email
            instance.user.username = email
            instance.user.save()
        return instance


class ProfileCategorySerializer(serializers.ModelSerializer):

    price = serializers.CharField(max_length=14, required=False)

    class Meta:
        model = models.ProfileCategory
        fields = ['profile', 'category', 'type_pay', 'price']

    def validate_price(self, value):
        return value.replace('.', '').replace(',', '.')

    def validate(self, data):
        queryset = self.Meta.model.objects.filter(profile=data.get('profile'), category=data.get('category'))
        if not self.instance and queryset.exists():
            raise serializers.ValidationError('Categoria já cadastrada!', code='invalid')
        return data


class ProfileCategorySerializerRetrieve(serializers.ModelSerializer):

    category = CategorySerializerRetrieve()
    type_pay = TypePaySerializerRetrieve()

    class Meta:
        model = models.ProfileCategory
        fields = ['id', 'category', 'type_pay', 'price']


class AddressRetrieve(serializers.Serializer):

    lat = serializers.FloatField()
    lng = serializers.FloatField()
    zipcode = serializers.SerializerMethodField()
    district = serializers.CharField()
    city = CitySerializerRetrieve()
    address = serializers.CharField()
    number = serializers.CharField()
    complement = serializers.CharField()

    def get_zipcode(self, obj):
        return obj.get_zipcode_formated


class ProfileSerializerRetrieve(serializers.ModelSerializer):

    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    cpf = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    categories = ProfileCategorySerializerRetrieve(many=True)

    class Meta:
        model = models.Profile
        fields = ['id', 'first_name', 'last_name', 'cpf', 'types', 'email', 'phone', 'photo', 'rating', 'birthday',
                  'address', 'categories']

    def get_first_name(self, obj):
        return obj.user.first_name

    def get_last_name(self, obj):
        return obj.user.last_name

    def get_email(self, obj):
        return obj.user.email

    def get_phone(self, obj):
        return obj.get_phone_formated

    def get_cpf(self, obj):
        return obj.get_cpf_formated

    def get_address(self, obj):
        return AddressRetrieve(obj).data


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Review
        fields = ['from_profile', 'to_profile', 'note', 'text']


class ReviewSerializerRetrieve(serializers.ModelSerializer):

    to_profile = ProfileSerializerRetrieve()
    from_profile = ProfileSerializerRetrieve()

    class Meta:
        model = models.Review
        fields = ['id', 'from_profile', 'to_profile', 'note', 'text']


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Gallery
        fields = ['profile', 'image']


class GallerySerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.Gallery
        fields = ['id', 'image']


class ServiceImageSerializer(serializers.Serializer):

    file = serializers.ImageField()


class ServiceImageSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.ServiceImage
        fields = ['image']


class ServiceSerializer(serializers.ModelSerializer):

    CHOICES = [
        (models.Service.DONE, 'Realizado'),
        (models.Service.APPROVED, 'Aprovado'),
        (models.Service.CANCELED, 'Cancelado'),
        (models.ServiceProfessional.RECUSED, 'Recusado'),
        (models.Service.REQUESTED, 'Aguardando aprovação')
    ]

    date = serializers.CharField()
    zipcode = serializers.CharField(max_length=9)
    images = ServiceImageSerializer(many=True, required=False)
    status = serializers.ChoiceField(choices=CHOICES, default=models.Service.REQUESTED)
    text_cancel = serializers.CharField(required=False)

    class Meta:
        model = models.Service
        fields = ['category', 'professional', 'client', 'lat', 'lng', 'zipcode', 'city', 'address', 'number',
                  'district', 'complement', 'date', 'time', 'observation', 'images', 'status', 'text_cancel']

    def validate_zipcode(self, value):
        return ZipCode(value).cleaning()

    def validate_date(self, value):
        return value[:10]

    def create(self, validated_data):
        images = validated_data.pop('images', [])
        instance = self.Meta.model._default_manager.create(**validated_data)

        models.ServiceProfessional.objects.create(service=instance, professional=instance.professional)
        for image in images:
            models.ServiceImage.objects.create(service=instance, image=image.get('file'))
        return instance

    def update(self, instance, validated_data):
        status = validated_data.get('status')
        text_cancel = validated_data.get('text_cancel')

        if status and status != models.Service.CANCELED:
            models.ServiceProfessional.objects.filter(
                service=instance, professional=instance.professional
            ).update(status=status, observation=text_cancel)

        if status == models.ServiceProfessional.RECUSED:
            validated_data.pop('status')

            professionals = models.ServiceProfessional.objects.filter(
                service=instance.id).values_list('professional_id')
            queryset = models.Profile.objects.filter(
                types=models.Profile.PROFESSIONAL, expiration__gte=datetime.now().date(),
                categories__category=instance.category).exclude(pk__in=professionals)

            title = 'Serviço Recusado'
            message = message = 'O serviço do dia {} {}, foi recusado. '.format(
                instance.date.strftime('%d/%m/%Y'), instance.time)

            if queryset.exists():
                status = models.Service.REQUESTED
                professional = queryset.first()
                instance.professional = professional
                models.ServiceProfessional.objects.create(service=instance, professional=professional)
                message += 'Mas fique tranquilo, já encontramos o profissional {} '\
                           'para o serviço'.format(instance.professional)
            else:
                status = models.Service.CANCELED
                message += 'Infelizmente seu serviço foi cancelado, pois não encontramos '\
                           'um profissional para seu serviço'

            instance.status = status
            instance.save()

            player_ids = [instance.client.onesignal]
            PushNotification().send_players(player_ids, title, message)

        return super().update(instance, validated_data)


class ServiceSerializerRetrieve(serializers.ModelSerializer):

    category = CategorySerializerRetrieve()
    professional = ProfileSerializerRetrieve()
    client = ProfileSerializerRetrieve()
    zipcode = serializers.SerializerMethodField()
    city = CitySerializerRetrieve()
    images = ServiceImageSerializerRetrieve(many=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = models.Service
        fields = ['id', 'category', 'professional', 'client', 'lat', 'lng', 'zipcode', 'city', 'address', 'number',
                  'district', 'complement', 'date', 'time', 'observation', 'images', 'status']

    def get_zipcode(self, obj):
        return obj.get_zipcode_formated

    def get_status(self, obj):
        return {'text': obj.get_status_display(), 'value': obj.status}
