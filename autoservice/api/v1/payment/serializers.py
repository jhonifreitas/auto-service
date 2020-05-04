from rest_framework import serializers

from autoservice.customer.models import PayRequest


class CardSerializer(serializers.Serializer):

    class Meta:
        fields = ['number', 'name', 'cpf', 'month', 'year', 'cvv', 'instaments']


class PayRequestSerializer(serializers.ModelSerializer):

    card = CardSerializer(required=False)
    sender_hash = serializers.CharField()

    class Meta:
        model = PayRequest
        fields = ['code', 'card', 'payment_link', 'payment_type', 'sender_hash', 'status']
