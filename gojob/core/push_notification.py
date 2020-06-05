import json
import requests

from django.conf import settings


class PushNotification(object):

    def __init__(self):
        self.header = {"Content-Type": "application/json; charset=utf-8"}

        self.payload = {
            "app_id": settings.ONESIGNAL_APP_ID,
            "headings": {"en": ''},
            "contents": {"en": ''}
        }

    def send_all(self, title, message, params):
        self.header['Authorization'] = "Basic "+settings.ONESIGNAL_REST_API_KEY
        self.payload['included_segments'] = ["All"]
        self.payload.get('headings')['en'] = title
        self.payload.get('contents')['en'] = message
        self.payload['data'] = params
        return self.send()

    def send_players(self, player_ids, title, message, params={}):
        self.payload['include_player_ids'] = player_ids
        self.payload.get('headings')['en'] = title
        self.payload.get('contents')['en'] = message
        self.payload['data'] = params
        return self.send()

    def send(self):
        try:
            response = requests.post(
                "https://onesignal.com/api/v1/notifications",
                headers=self.header,
                data=json.dumps(self.payload)
            ).json()
        except Exception as e:
            response = e.response.json()

        return response
