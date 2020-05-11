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

    def set_pre_approval(self, config):
        self.pg.pre_approval = {
            'charge': 'AUTO',
            'name': 'Assinatura do Aplicativo Auto Service',
            'details': 'Todo dia 10 de cada mês será cobrado o valor de R$ {}'.format(config.value),
            'amount_per_payment': config.value,
            'period': 'MONTHLY'
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

    def credit_card(self, card, profile):
        config = Config.objects.first()
        self.pg.payment.update({'method': 'creditCard'})
        self.pg.credit_card = {
            'credit_card_token': card.get('card_token'),
            'installment_quantity': 1,
            'installment_value': config.value,
            'no_interest_installment_quantity': config.no_interest_installment,

            'card_holder_name': card.get('card_name'),
            'card_holder_cpf': card.get('card_cpf'),

            'billing_address_street': profile.address,
            'billing_address_number': profile.number,
            'billing_address_complement': profile.complement,
            'billing_address_district': profile.district,
            'billing_address_postal_code': profile.zipcode,
            'billing_address_city': profile.city.name,
            'billing_address_state': profile.city.state.uf,
        }
        return self.checkout()

    def checkout(self):
        config = Config.objects.first()
        self.pg.notification_url = '{}{}'.format(self.host, self.notification_url)
        self.set_pre_approval(config)
        self.pg.items = [{
            "id": 1,
            "description": 'Assinatura do Aplicativo Auto Service',
            "amount": config.value,
            "quantity": 1
        }]
        return self.pg.checkout(transparent=True)
