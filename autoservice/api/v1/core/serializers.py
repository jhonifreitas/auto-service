from rest_framework import serializers

from autoservice.core import models


class StateSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.State
        fields = ['id', 'name', 'uf']


class CitySerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.City
        fields = ['id', 'name']


class ServiceSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.Service
        fields = ['id', 'name', 'icon']
