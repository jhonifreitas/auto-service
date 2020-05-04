from pagseguro import PagSeguro

from django.conf import settings
from django.urls import reverse_lazy

from autoservice.core.models import Config


class Transcation:

    host = 'http://45.132.242.190'
    use_shipping = False
    sandbox = settings.PAGSEGURO_SANDBOX
    notification_url = reverse_lazy('api.v1:pag-notification')

    def __init__(self):
        self.pg = PagSeguro(email=settings.PAGSEGURO_EMAIL, token=settings.PAGSEGURO_TOKEN, config=self.get_config())
        self.pg.payment = {'mode': 'default'}

    def set_senderHash(self, senderHash):
        self.senderHash = senderHash

    def set_sender(self, data):
        self.pg.sender = {
            "name": data.user.get_full_name(),
            "area_code": data.phone[:2],
            "phone": data.phone[2:],
            "email": data.user.email,
            "hash": self.senderHash,
            "cpf": data.cpf,
        }

    def get_config(self):
        return {'sandbox': self.sandbox, 'USE_SHIPPING': self.use_shipping}

    def get_session(self):
        return self.pg.transparent_checkout_session()

    def cancel(self, code):
        url = f'{self.pg.config.QUERY_TRANSACTION_URL}/cancels'
        self.pg.data.update({'transactionCode': code})
        return self.pg.post(url)

    def ticket(self, data):
        self.pg.payment.update({'method': 'boleto'})
        return self.checkout()

    def get_notification(self, code):
        return self.pg.check_notification(code)

    def credit_card(self, data):
        config = Config.objects.first()
        self.pg.payment.update({'method': 'creditCard'})
        self.pg.credit_card = {
            'credit_card_token': data.get('card_token'),
            'installment_quantity': data.get('card_installment_quantity'),
            'installment_value': data.get('card_installment_value'),
            'no_interest_installment_quantity': config.no_interest_installment,

            'card_holder_name': data.get('card_name'),
            'card_holder_cpf': data.get('card_cpf'),

            'billing_address_street': data.get('address'),
            'billing_address_number': data.get('number'),
            'billing_address_complement': data.get('complement'),
            'billing_address_district': data.get('district'),
            'billing_address_postal_code': data.get('postal_code'),
            'billing_address_city': data.get('city'),
            'billing_address_state': data.get('state'),
        }
        return self.checkout()

    def checkout(self):
        config = Config.objects.first()
        self.pg.notification_url = '{}{}'.format(self.host, self.notification_url)

        self.pg.items = [{
            "id": self.ad.pk,
            "description": self.ad.earth.name,
            "amount": config.value,
            "quantity": 1
        }]
        return self.pg.checkout(transparent=True)
