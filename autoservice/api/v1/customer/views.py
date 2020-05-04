from datetime import datetime

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed

from django.shortcuts import get_object_or_404

from autoservice.api.v1.customer import serializers
from autoservice.api.v1.auth.serializers import LoginSerializer


class ProfileViewSet(viewsets.ViewSet):

    serializer_class = serializers.ProfileSerializer
    serializer_class_login = LoginSerializer
    serializer_class_retrieve = serializers.ProfileSerializerRetrieve

    def login(self, post_data):
        data = {
            'username': post_data.get('email'),
            'password': post_data.get('password'),
            'onesignal': post_data.get('onesignal'),
        }
        serializer = self.serializer_class_login(data=data)
        if serializer.is_valid():
            return Response(serializer.get_data(self.request), status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request):
        data = request.POST.copy()
        photo = request.data.get('photo')
        if photo:
            data.update({'photo': photo})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return self.login(data)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = self.serializer_class(instance=request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AutonomousViewSet(ProfileViewSet):

    def get_object(self):
        return get_object_or_404(self.serializer_class_retrieve.Meta.model, pk=self.kwargs.get('pk'))

    def get_queryset(self):
        return self.serializer_class_retrieve.Meta.model.objects.filter(
            types=self.serializer_class_retrieve.Meta.model.AUTONOMOUS, expiration__gte=datetime.now().date(),
            services__service__id=self.kwargs.get('service_id'))

    def list(self, request, service_id):
        context = {'request': request}
        return Response(self.serializer_class_retrieve(
            self.get_queryset(), many=True, context=context).data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        context = {'request': request}
        return Response(self.serializer_class_retrieve(
            self.get_object(), context=context).data, status=status.HTTP_200_OK)


class ProfileServiceViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ProfileServiceSerializer
    serializer_class_retrieve = serializers.ProfileServiceSerializerRetrieve

    def get_queryset(self):
        return self.request.user.profile.services.all()

    def list(self, request):
        context = {'request': request}
        return Response(self.serializer_class_retrieve(
            self.get_queryset(), many=True, context=context).data, status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data.copy()
        data.update({'profile': request.user.profile.pk})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        data = request.data.copy()
        data.update({'profile': request.user.profile.pk})
        serializer = self.serializer_class(self.get_object(), data=data)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ReviewSerializer
    serializer_class_retrieve = serializers.ReviewSerializerRetrieve

    def get_queryset(self):
        return self.request.user.profile.review_from.all()

    def list(self, request):
        raise MethodNotAllowed('GET')

    def create(self, request):
        data = request.data.copy()
        data.update({'from_profile': request.user.profile.pk})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        data = request.data.copy()
        data.update({'from_profile': request.user.profile.pk})
        serializer = self.serializer_class(self.get_object(), data=data)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class JobDoneViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.JobDoneSerializer
    serializer_class_retrieve = serializers.JobDoneSerializerRetrieve

    def get_queryset(self):
        return self.request.user.profile.jobs_done.all()

    def list(self, request):
        context = {'request': request}
        return Response(
            self.serializer_class_retrieve(self.get_queryset(), many=True, context=context).data,
            status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data.copy()
        data.update({'profile': request.user.profile.pk})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk):
        data = request.data.copy()
        data.update({'profile': request.user.profile.pk})
        serializer = self.serializer_class(self.get_object(), data=data)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_201_CREATED)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
