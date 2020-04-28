from base64 import b64encode
from datetime import datetime
from rest_framework import serializers
from itsdangerous import TimedJSONWebSignatureSerializer

from django.conf import settings
from django.contrib.auth.models import User

from autoservice.customer import models
from autoservice.api.v1.customer.serializers import ProfileSerializerRetrieve, AutonomousSerializerRetrieve


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    def validate(self, data):
        try:
            self.user = User.objects.get(username=data.get('username'))
            if (not self.user.check_password(data.get('password')) or
                    hasattr(self.user, 'profile') and hasattr(self.user, 'autonomous')):
                raise serializers.ValidationError('Usuário ou senha não conferem.', code='invalid')
            if hasattr(self.user, 'autonomous') and self.user.autonomous.expiration < datetime.now().date():
                raise serializers.ValidationError('Usuário expirado!', code='invalid')
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuário ou senha não conferem.', code='invalid')

        return data

    def get_token(self):
        serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=settings.EXPIRES_IN)
        token = serializer.dumps({'username': self.validated_data.get('username'),
                                  'password': self.validated_data.get('password')})
        return b64encode(token)

    def get_data(self, request):
        context = {'request': request}
        data = {
            'token': self.get_token()
        }
        if hasattr(self.user, 'profile'):
            data['profile'] = ProfileSerializerRetrieve(
                models.Profile.objects.get(id=self.user.profile.pk), context=context).data
        if hasattr(self.user, 'autonomous'):
            data['autonomous'] = AutonomousSerializerRetrieve(
                models.Autonomous.objects.get(id=self.user.autonomous.pk), context=context).data
        return data
