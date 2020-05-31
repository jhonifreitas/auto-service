from datetime import datetime, timedelta

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from autoservice.customer.models import Profile
from autoservice.api.v1.payment import serializers
from autoservice.api.v1.payment.pagseguro import Transcation
from autoservice.api.v1.customer.serializers import ProfileSerializerRetrieve


class PaymentViewSet(viewsets.ViewSet):

    pagseguro = Transcation()
    serializer_class_retrieve = ProfileSerializerRetrieve

    def get_object(self, code):
        return get_object_or_404(serializers.PayRequestSerializer.Meta.model, code=code)

    def get_session(self, request):
        return Response({'session_id': self.pagseguro.get_session()}, status=status.HTTP_200_OK)

    def pay(self, request):
        data = request.data.copy()
        profile = request.user.profile
        data.update({'profile': profile.pk})
        serializer = serializers.PayRequestSerializer(data=data)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            self.pagseguro.set_senderHash(validated_data.get('sender_hash'))
            self.pagseguro.set_sender(profile)

            if validated_data.get('payment_type') == 'ticket':
                result = self.pagseguro.ticket(validated_data)
            elif validated_data.get('payment_type') == 'credit_card':
                result = self.pagseguro.credit_card(validated_data, profile)

            if not result.errors:
                code = result.transaction.get('code')
                payment_link = result.transaction.get('paymentLink')
                serializer.save(code=code, payment_link=payment_link)

                profile.types = Profile.PROFESSIONAL
                profile.expiration = datetime.now() + timedelta(days=30)
                profile.save()
                context = {'request': request}
                return Response(
                    self.serializer_class_retrieve(profile, context=context).data, status=status.HTTP_200_OK)
            error = {
                'error': 'Erro ao gerar pagamento!',
                'pagseguro': result.errors
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def notification(self, request):
        code = request.data.get('notificationCode')
        result = self.pagseguro.get_notification(code)
        if not result.errors:
            obj = self.get_object(result.code)
            obj.status = result.status
            obj.save()

            return Response({'ok': 'Atualizado!'}, status=status.HTTP_200_OK)
        return Response({'errors': result.errors}, status=status.HTTP_200_OK)
