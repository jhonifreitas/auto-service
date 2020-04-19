from rest_framework import serializers

from django.contrib.auth.models import User

from autoservice.customer import models
from autoservice.api.v1.core.serializers import CitySerializerRetrieve


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password']

    def create(self, validated_data):
        instance = super().create(validated_data)
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Review
        fields = ['to_autonomous', 'note', 'text']


class ReviewSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.Review
        fields = ['id', 'from_profile', 'to_autonomous', 'note', 'text']


class AutonomousServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.AutonomousService
        fields = ['service', 'week', 'start_hour', 'end_hour', 'type_pay', 'price']


class AutonomousServiceSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.AutonomousService
        fields = ['id', 'service', 'week', 'start_hour', 'end_hour', 'type_pay', 'price']


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Profile
        fields = ['user', 'photo', 'city', 'phone']


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


class AutonomousSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Autonomous
        fields = ['user', 'city', 'phone', 'photo', 'birthday', 'about']


class AutonomousSerializerRetrieve(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    city = CitySerializerRetrieve()
    reviews = ReviewSerializerRetrieve(many=True)
    services = AutonomousServiceSerializerRetrieve(many=True)

    class Meta:
        model = models.Autonomous
        fields = ['id', 'name', 'email', 'city', 'phone', 'photo', 'rating', 'birthday', 'about', 'reviews',
                  'services']

    def get_name(self, obj):
        return obj.user.get_full_name()

    def get_email(self, obj):
        return obj.user.email
