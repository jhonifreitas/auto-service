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


class ServiceSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.Service
        fields = ['id', 'name', 'icon']


class WeekSerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.Week
        fields = ['id', 'name']


class TypePaySerializerRetrieve(serializers.ModelSerializer):

    class Meta:
        model = models.TypePay
        fields = ['id', 'name']
