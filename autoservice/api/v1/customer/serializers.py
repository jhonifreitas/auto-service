from rest_framework import serializers

from django.contrib.auth.models import User

from autoservice.customer import models
from autoservice.core.utils import Phone
from autoservice.api.v1.core.serializers import (CitySerializerRetrieve, ServiceSerializerRetrieve,
                                                 TypePaySerializerRetrieve, WeekSerializerRetrieve)


class ProfileSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(max_length=15)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    birthday = serializers.CharField(required=False)
    password = serializers.CharField()

    class Meta:
        model = models.Profile
        fields = ['name', 'email', 'photo', 'city', 'phone', 'birthday', 'about', 'password']

    def validate_phone(self, value):
        return Phone(value).cleaning()

    def get_first_name(self, name):
        list_name = name.split(' ')
        return list_name[0]

    def validate_birthday(self, value):
        return value[:10]

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


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Review
        fields = ['from_profile', 'to_profile', 'note', 'text']


class ReviewSerializerRetrieve(serializers.ModelSerializer):

    from_profile = serializers.SerializerMethodField()

    class Meta:
        model = models.Review
        fields = ['id', 'from_profile', 'note', 'text', 'updated_at']

    def get_from_profile(self, obj):
        return {
            'id': obj.from_profile.id,
            'name': obj.from_profile.user.get_full_name()
        }


class ProfileServiceSerializer(serializers.ModelSerializer):

    start_hour = serializers.CharField()
    end_hour = serializers.CharField()
    price = serializers.CharField(max_length=14, required=False)

    class Meta:
        model = models.ProfileService
        fields = ['profile', 'service', 'week', 'start_hour', 'end_hour', 'type_pay', 'price']

    def validate_start_hour(self, value):
        return value[11:]

    def validate_end_hour(self, value):
        return value[11:]

    def validate_price(self, value):
        return value.replace('.', '').replace(',', '.')


class ProfileServiceSerializerRetrieve(serializers.ModelSerializer):

    service = ServiceSerializerRetrieve()
    type_pay = TypePaySerializerRetrieve()
    week = WeekSerializerRetrieve(many=True)

    class Meta:
        model = models.ProfileService
        fields = ['id', 'service', 'week', 'start_hour', 'end_hour', 'type_pay', 'price']


class JobDoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.JobDone
        fields = ['profile', 'service', 'image']


class JobDoneSerializerRetrieve(serializers.ModelSerializer):

    service = ServiceSerializerRetrieve()

    class Meta:
        model = models.JobDone
        fields = ['id', 'service', 'image']


class ProfileSerializerRetrieve(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    city = CitySerializerRetrieve()
    reviews = ReviewSerializerRetrieve(many=True, source='review_to')
    services = ProfileServiceSerializerRetrieve(many=True)
    jobs_done = JobDoneSerializerRetrieve(many=True)

    class Meta:
        model = models.Profile
        fields = ['id', 'name', 'types', 'email', 'city', 'phone', 'photo', 'rating', 'birthday', 'about', 'reviews',
                  'services', 'jobs_done']

    def get_name(self, obj):
        return obj.user.get_full_name()

    def get_email(self, obj):
        return obj.user.email

    def get_phone(self, obj):
        return obj.get_phone_formated
