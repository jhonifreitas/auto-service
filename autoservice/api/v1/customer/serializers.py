from rest_framework import serializers

from django.contrib.auth.models import User

from autoservice.customer import models
from autoservice.core.utils import Phone
from autoservice.api.v1.core.serializers import (CitySerializerRetrieve, ServiceSerializerRetrieve,
                                                 TypePaySerializerRetrieve)


class ProfileSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=15)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = models.Profile
        fields = ['name', 'email', 'photo', 'city', 'phone', 'password']

    def validate_phone(self, value):
        return Phone(value).cleaning()

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

        instance.user.fisrt_name = self.get_first_name(name)
        instance.user.last_name = self.get_last_name(name)
        instance.user.save()
        return instance


class ProfileSerializerRetrieve(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    city = CitySerializerRetrieve()

    class Meta:
        model = models.Profile
        fields = ['id', 'name', 'email', 'photo', 'city', 'phone']

    def get_name(self, obj):
        return obj.user.get_full_name()

    def get_email(self, obj):
        return obj.user.email


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Review
        fields = ['to_autonomous', 'note', 'text']


class ReviewSerializerRetrieve(serializers.ModelSerializer):

    from_profile = ProfileSerializerRetrieve()

    class Meta:
        model = models.Review
        fields = ['id', 'from_profile', 'note', 'text']


class AutonomousServiceSerializer(serializers.ModelSerializer):

    start_hour = serializers.CharField()
    end_hour = serializers.CharField()
    price = serializers.CharField(max_length=14)

    class Meta:
        model = models.AutonomousService
        fields = ['autonomous', 'service', 'week', 'start_hour', 'end_hour', 'type_pay', 'price']

    def validate_start_hour(self, value):
        return value[11:]

    def validate_end_hour(self, value):
        return value[11:]

    def validate_price(self, value):
        return value.replace('.', '').replace(',', '.')


class AutonomousServiceSerializerRetrieve(serializers.ModelSerializer):

    service = ServiceSerializerRetrieve()
    type_pay = TypePaySerializerRetrieve()

    class Meta:
        model = models.AutonomousService
        fields = ['id', 'service', 'week', 'start_hour', 'end_hour', 'type_pay', 'price']


class AutonomousSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=15)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField()
    birthday = serializers.CharField()

    class Meta:
        model = models.Autonomous
        fields = ['name', 'email', 'city', 'phone', 'photo', 'birthday', 'about', 'password']

    def validate_phone(self, value):
        return Phone(value).cleaning()

    def validate_birthday(self, value):
        return value[:10]

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

        instance.user.fisrt_name = self.get_first_name(name)
        instance.user.last_name = self.get_last_name(name)
        instance.user.save()
        return instance


class AutonomousSerializerRetrieve(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    city = CitySerializerRetrieve()
    reviews = ReviewSerializerRetrieve(many=True, source='review_to')
    services = AutonomousServiceSerializerRetrieve(many=True, source='autonomous_services')

    class Meta:
        model = models.Autonomous
        fields = ['id', 'name', 'email', 'city', 'phone', 'photo', 'rating', 'birthday', 'about', 'reviews',
                  'services']

    def get_name(self, obj):
        return obj.user.get_full_name()

    def get_email(self, obj):
        return obj.user.email
