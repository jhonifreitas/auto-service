from base64 import b64encode
from datetime import datetime
from rest_framework import serializers
from itsdangerous import TimedJSONWebSignatureSerializer

from django.conf import settings

from autoservice.customer.models import Profile
from autoservice.api.v1.customer.serializers import ProfileSerializerRetrieve


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    def validate(self, data):
        try:
            self.profile = Profile.objects.get(user__username=data.get('username'))
            if not self.profile.user.check_password(data.get('password')):
                raise serializers.ValidationError('Usuário ou senha não conferem.', code='invalid')
            if self.profile.types == Profile.PROFESSIONAL and self.profile.expiration < datetime.now().date():
                raise serializers.ValidationError('Usuário expirado!', code='invalid')
        except Profile.DoesNotExist:
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
            'token': self.get_token(),
            'profile': ProfileSerializerRetrieve(self.profile, context=context).data
        }
        return data
