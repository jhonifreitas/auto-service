from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator

from autoservice.api.v1.auth.serializers import LoginSerializer


class LoginViewSet(viewsets.ViewSet):

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            return Response(serializer.get_data(request), status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetViewSet(viewsets.ViewSet):

    def post(self, request):
        if User.objects.filter(email=request.data.get('email')).exists():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': None,
                'email_template_name': 'registration/password_reset_email.html',
                'subject_template_name': 'registration/password_reset_subject.txt',
                'request': request,
                'html_email_template_name': None,
                'extra_email_context': None,
            }
            form = PasswordResetForm(request.data)
            if form.is_valid():
                form.save(**opts)
                return Response({'ok': 'E-mail enviado com sucesso!'}, status=status.HTTP_200_OK)
        return Response({'error': 'E-mail inválido!'}, status=status.HTTP_400_BAD_REQUEST)
