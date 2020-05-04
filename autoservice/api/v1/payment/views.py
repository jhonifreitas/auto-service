from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from autoservice.api.v1.payment import serializers
from autoservice.api.v1.payment.pagseguro import Transcation


class PaymentViewSet(viewsets.ViewSet):

    pagseguro = Transcation()

    def get_object(self, code):
        return get_object_or_404(serializers.PayRequestSerializer.Meta.model, code=code)

    def get_session(self, request):
        return Response({'session_id': self.pagseguro.get_session()}, status=status.HTTP_200_OK)

    def pay(self, request):
        data = request.data.copy()
        serializer = serializers.PayRequestSerializer(data=data)
        self.pagseguro.set_senderHash(data.get('sender_hash'))
        self.pagseguro.set_sender(request.user.profile)

        if data.get('payment_type') == 'ticket':
            result = self.pagseguro.ticket(data)
        elif data.get('payment_type') == 'credit_card':
            result = self.pagseguro.credit_card(data)

        error = {'errors': serializer.errors}
        if result:
            if not result.errors and serializer.is_valid():
                data.update({'code': result.transaction.get('code')})
                data.update({'payment_link': result.transaction.get('paymentLink')})
                serializer.save()
                return Response({'success': True}, status=status.HTTP_200_OK)
            if result.errors:
                error = {
                    'error': 'Erro ao gerar pagamento!',
                    'pagseguro': result.errors
                }
        return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def notification(self, request):
        code = request.data.get('notificationCode')
        result = self.pagseguro.get_notification(code)
        if not result.errors:
            obj = self.get_object(code)
            obj.status = result.status
            obj.save()

            return Response({'ok': 'Atualizado!'}, status=status.HTTP_200_OK)
        return Response({'errors': result.errors}, status=status.HTTP_200_OK)
