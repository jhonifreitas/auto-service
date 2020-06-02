from rest_framework import serializers

from django.contrib.auth.models import User

from autoservice.customer import models
from autoservice.core.utils import Phone, ZipCode, CPF
from autoservice.api.v1.core.serializers import (CitySerializerRetrieve, CategorySerializerRetrieve,
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
        fields = ['name', 'email', 'cpf', 'photo', 'city', 'phone', 'birthday', 'zipcode', 'address',
                  'district', 'number', 'complement', 'password']

    def validate_phone(self, value):
        return Phone(value).cleaning()

    def validate_cpf(self, value):
        return CPF(value).cleaning()

    def validate_zipcode(self, value):
        return ZipCode(value).cleaning()

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
        if name:
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


class GallerySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Gallery
        fields = ['profile', 'category', 'image']


class GallerySerializerRetrieve(serializers.ModelSerializer):

    category = CategorySerializerRetrieve()

    class Meta:
        model = models.Gallery
        fields = ['id', 'category', 'image']


class AddressRetrieve(serializers.Serializer):

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
    reviews = ReviewSerializerRetrieve(many=True, source='review_to')
    categories = ProfileCategorySerializerRetrieve(many=True)
    gallery = GallerySerializerRetrieve(many=True)

    class Meta:
        model = models.Profile
        fields = ['id', 'first_name', 'last_name', 'cpf', 'types', 'email', 'phone', 'photo', 'rating', 'birthday',
                  'address', 'reviews', 'categories', 'gallery']

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
