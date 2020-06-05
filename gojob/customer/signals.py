from datetime import datetime

from gojob.core.push_notification import PushNotification


def pre_save_service(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
        params = {'service_id': instance.pk}
        if obj.status != instance.status and instance.status != sender.REQUESTED:
            title = 'Serviço '
            message = 'O serviço do dia {} {}'.format(instance.date.strftime('%d/%m/%Y'), instance.time)
            player_ids = [instance.client.onesignal]

            if instance.status == sender.DONE:
                title += 'Realizado'
                message += ', foi realizado, deixe sua avaliação ao profissional'
            elif instance.status == sender.APPROVED:
                title += 'Aprovado'
                message += ', foi aprovado. Agora você pode chamar o profissional pelo whatsapp'
            elif instance.status == sender.CANCELED:
                title += 'Cancelado'
                message += ', foi cancelado'
                player_ids = [instance.professional.onesignal]

            PushNotification().send_players(player_ids, title, message, params)
        if obj.date != instance.date or obj.time != instance.time:
            date = datetime.strptime(instance.date, '%Y-%m-%d').date().strftime('%d/%m/%Y')
            title = 'Data do serviço alterada'
            message = 'A data do serviço foi alterada de {} {} para {} {}'.format(
                obj.date.strftime('%d/%m/%Y'), obj.time, date, instance.time)
            player_ids = [instance.professional.onesignal, instance.client.onesignal]
            PushNotification().send_players(player_ids, title, message, params)
    except sender.DoesNotExist:
        pass


def post_save_service(sender, instance, created, **kwargs):
    if created and instance.professional.onesignal:
        date = datetime.strptime(instance.date, '%Y-%m-%d').date().strftime('%d/%m/%Y')
        title = 'Nova solicitação de serviço'
        message = 'Você tem uma nova solicitação de serviço para o dia {}'.format(date)
        params = {'service_id': instance.pk}
        PushNotification().send_players([instance.professional.onesignal], title, message, params)


def post_delete_service(sender, instance, **kwargs):
    title = 'Serviço cancelado'
    message = 'O serviço do dia {} {}, foi cancelado'.format(instance.date.strftime('%d/%m/%Y'), instance.time)
    PushNotification().send_players([instance.professional.onesignal], title, message)
