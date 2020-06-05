from datetime import datetime, timedelta

from pagseguro import PagSeguro

from django.conf import settings
from django.urls import reverse_lazy

from gojob.core.models import Config


class Transcation:

    config = None
    use_shipping = False
    host = 'http://45.132.242.190'
    sandbox = settings.PAGSEGURO_SANDBOX
    notification_url = reverse_lazy('api.v1:pag-notification')

    def __init__(self):
        self.pg = PagSeguro(email=settings.PAGSEGURO_EMAIL, token=settings.PAGSEGURO_TOKEN, config=self.get_config())
        self.pg.payment = {'mode': 'default'}
        self.config = Config.objects.first()

    def set_senderHash(self, senderHash):
        self.senderHash = senderHash

    def set_notification_url(self):
        self.pg.notification_url = '{}{}'.format(self.host, self.notification_url)

    def set_sender(self, profile):
        self.pg.sender = {
            "name": profile.user.get_full_name(),
            "email": profile.user.email,
            "hash": self.senderHash,
            "phone": {
                "areaCode": profile.phone[:2],
                "number": profile.phone[2:],
            },
            "documents": [{
                "type": "CPF",
                "value": profile.cpf
            }],
            'address': {
                'street': profile.address,
                'number': profile.number,
                'complement': profile.complement,
                'district': profile.district,
                'city': profile.city.name,
                'state': profile.city.state.uf,
                'postalCode': profile.zipcode,
                'country': 'BRA'
            }
        }

    def get_config(self):
        return {'sandbox': self.sandbox, 'USE_SHIPPING': self.use_shipping}

    def get_session(self):
        return self.pg.transparent_checkout_session()

    def get_notification(self, code):
        return self.pg.check_notification(code)

    def cancel(self, code):
        url = f'{self.pg.config.QUERY_TRANSACTION_URL}/cancels'
        self.pg.data.update({'transactionCode': code})
        return self.pg.post(url)

    def ticket(self, data):
        date = datetime.now().date() + timedelta(days=self.config.trial_period)
        self.set_notification_url()
        self.pg.ticket = {
            'firstDueDate': date.isoformat(),
            'numberOfPayments': 1,
            'amount': str(self.config.value),
            'description': self.config.plan_name,
        }
        return self.pg.generate_ticket()

    def credit_card(self, card, profile):
        self.set_notification_url()
        self.pg.code = self.config.plan_code
        self.pg.payment.update({'method': 'creditCard'})
        self.pg.credit_card = {
            'token': card.get('card_token'),
            'holder': {
                'name': card.get('card_name'),
                'birthDate': profile.birthday.strftime('%d/%m/%Y'),
                'documents': [{
                    'type': 'CPF',
                    'value': profile.cpf
                }],
                "phone": {
                    "areaCode": profile.phone[:2],
                    "number": profile.phone[2:],
                }
            }
        }
        return self.pg.pre_approval_ask()

    def create_new_plan(self):
        self.pg.pre_approval = {
            'charge': 'AUTO',
            'name': self.config.plan_name,
            'details': self.config.plan_description,
            'amount_per_payment': self.config.value,
            'trial_period_duration': self.config.trial_period,
            'period': 'MONTHLY'
        }
        return self.pg.pre_approval_request()
