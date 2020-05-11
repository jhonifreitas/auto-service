from rest_framework import serializers

from autoservice.core.utils import CPF
from autoservice.customer.models import PayRequest, Profile


class PayRequestSerializer(serializers.Serializer):

    sender_hash = serializers.CharField()
    payment_type = serializers.CharField()
    code = serializers.CharField(required=False)
    payment_link = serializers.URLField(required=False)
    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    # CARD
    card_token = serializers.CharField(required=False)
    card_number = serializers.CharField(required=False)
    card_name = serializers.CharField(required=False)
    card_cpf = serializers.CharField(max_length=14, required=False)
    card_month = serializers.IntegerField(required=False)
    card_year = serializers.IntegerField(required=False)
    card_cvv = serializers.IntegerField(required=False)

    def validate_card_cpf(self, value):
        return CPF(value).cleaning()

    def create(self, validated_data):
        validated_data.pop('sender_hash')
        validated_data.pop('card_token')
        validated_data.pop('card_number')
        validated_data.pop('card_name')
        validated_data.pop('card_cpf')
        validated_data.pop('card_month')
        validated_data.pop('card_year')
        validated_data.pop('card_cvv')
        return PayRequest.objects.create(**validated_data)
