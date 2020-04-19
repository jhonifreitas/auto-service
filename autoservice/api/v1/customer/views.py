from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from autoservice.customer import models
from autoservice.api.v1.customer import serializers
from autoservice.api.v1.auth.serializers import LoginSerializer


class ProfileViewSet(viewsets.ViewSet):

    serializer_class = serializers.UserSerializer
    serializer_class_login = LoginSerializer
    serializer_class_profile = serializers.ProfileSerializer

    def create_profile(self, data):
        serializer = self.serializer_class_profile(data=data)
        if serializer.is_valid():
            return serializer.save()
        return serializer

    def login(self, post_data):
        data = {
            'username': post_data.get('username'),
            'password': post_data.get('password'),
            'onesignal': post_data.get('onesignal'),
        }
        serializer = self.serializer_class_login(data=data)
        if serializer.is_valid():
            return Response(serializer.get_data(self.request), status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        data = request.POST.copy()
        data.update({'email': data.get('username')})
        if request.data.get('photo'):
            data.update({'photo': request.data.get('photo')})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            user = serializer.save()
            data.update({'user': user.pk})
            profile = self.create_profile(data)
            if isinstance(profile, models.Profile):
                return self.login(data)
            user.delete()
            return Response({'errors': profile.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AutonomousViewSet(ProfileViewSet):

    serializer_class_profile = serializers.AutonomousSerializer
    serializer_class_retrieve = serializers.AutonomousSerializerRetrieve

    def get_queryset(self):
        return self.serializer_class_retrieve.Meta.model.objects.filter(service_id=self.kwargs.get('service_id'))

    def list(self, request, service_id):
        context = {'request': request}
        return Response(self.serializer_class_retrieve(
            self.get_queryset(), many=True, context=context).data, status=status.HTTP_200_OK)
