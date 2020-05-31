from rest_framework import serializers

from autoservice.core import models


class StateSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.State
        fields = ['id', 'name', 'uf']


class CitySerializerRetrieve(serializers.ModelSerializer):

    state = StateSerializerRetrieve()

    class Meta:
        model = models.City
        fields = ['id', 'name', 'state']


class CategorySerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = ['id', 'name', 'image', 'icon']


class TypePaySerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.TypePay
        fields = ['id', 'name']


class ConfigSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.Config
        fields = ['trial_period', 'value']
