from datetime import datetime

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from django.db.models import Q
from django.shortcuts import get_object_or_404

from gojob.api.v1.customer import serializers
from gojob.api.v1.auth.serializers import LoginSerializer
from gojob.customer.models import Profile, Service, Review


class ProfileViewSet(viewsets.ViewSet):

    serializer_class = serializers.ProfileSerializer
    serializer_class_login = LoginSerializer
    serializer_class_retrieve = serializers.ProfileSerializerRetrieve

    def login(self, post_data):
        data = {
            'username': post_data.get('email'),
            'password': post_data.get('password')
        }
        onesignal = post_data.get('onesignal')
        if onesignal:
            data.update({'onesignal': onesignal})
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


class ProfessionalViewSet(viewsets.GenericViewSet):

    serializer_class = serializers.ProfileSerializerRetrieve

    def get_object(self):
        return get_object_or_404(self.serializer_class.Meta.model, pk=self.kwargs.get('pk'))

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            types=self.serializer_class.Meta.model.PROFESSIONAL, expiration__gte=datetime.now().date())

    def list(self, request):
        context = {'request': request}
        search = request.GET.get('search')
        category_id = request.GET.get('category_id')
        queryset = self.get_queryset()
        if category_id:
            queryset = queryset.filter(categories__category__id=category_id)
        if search:
            search = search.lower()
            queryset = queryset.filter(
                Q(categories__category__name__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(categories__category__hashtags__icontains=search)
            )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(self.serializer_class(queryset, many=True, context=context).data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk):
        context = {'request': request}
        return Response(self.serializer_class(self.get_object(), context=context).data, status=status.HTTP_200_OK)


class ProfileCategoryViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ProfileCategorySerializer
    serializer_class_retrieve = serializers.ProfileCategorySerializerRetrieve

    def get_queryset(self):
        return self.request.user.profile.categories.all()

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
        return self.serializer_class.Meta.model.objects.filter(to_profile=self.kwargs.get('pk'))

    def list(self, request, pk):
        context = {'request': request}
        return Response(
            self.serializer_class_retrieve(self.get_queryset(), many=True, context=context).data,
            status=status.HTTP_200_OK)

    def create(self, request):
        data = request.data.copy()
        data.update({'from_profile': request.user.profile.pk})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def pending(self, request):
        context = {'request': request}
        professionals = Service.objects.filter(
            status=Service.DONE, client=request.user.profile).values_list('professional')
        reviews = Review.objects.filter(
            from_profile=request.user.profile, to_profile__id__in=professionals).values_list('to_profile')
        queryset = Profile.objects.filter(id__in=professionals).exclude(id__in=reviews)
        return Response(
            serializers.ProfileSerializerRetrieve(queryset, many=True, context=context).data,
            status=status.HTTP_200_OK)


class GalleryViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.GallerySerializer
    serializer_class_retrieve = serializers.GallerySerializerRetrieve

    def get_queryset(self):
        return self.request.user.profile.gallery.all()

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


class ServiceViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.ServiceSerializer
    serializer_class_retrieve = serializers.ServiceSerializerRetrieve

    def get_queryset(self):
        if self.request.user.profile.types == Profile.PROFESSIONAL:
            queryset = self.request.user.profile.professional_services.all()
        else:
            queryset = self.request.user.profile.client_services.all()
        queryset.filter(date__lt=datetime.now().date()).update(status=self.serializer_class.Meta.model.DONE)
        return queryset

    def retrieve(self, request, pk):
        self.serializer_class = self.serializer_class_retrieve
        return super().retrieve(request, pk)

    def create(self, request):
        data = request.data.copy()
        data.update({'client': request.user.profile.pk})
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            obj = serializer.save()
            context = {'request': request}
            return Response(self.serializer_class_retrieve(obj, context=context).data, status=status.HTTP_200_OK)
        return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def requested(self, request):
        context = {'request': request}
        queryset = self.get_queryset().filter(
            Q(status=self.serializer_class.Meta.model.REQUESTED) |
            Q(status=self.serializer_class.Meta.model.APPROVED)
        )
        return Response(
            self.serializer_class_retrieve(queryset, many=True, context=context).data, status=status.HTTP_200_OK)

    def waiting(self, request):
        context = {'request': request}
        queryset = self.get_queryset().filter(status=self.serializer_class.Meta.model.REQUESTED)
        return Response(
            self.serializer_class_retrieve(queryset, many=True, context=context).data, status=status.HTTP_200_OK)

    def approved(self, request):
        context = {'request': request}
        queryset = self.get_queryset().filter(status=self.serializer_class.Meta.model.APPROVED)
        return Response(
            self.serializer_class_retrieve(queryset, many=True, context=context).data, status=status.HTTP_200_OK)

    def history(self, request):
        context = {'request': request}
        queryset = self.get_queryset().filter(
            Q(status=self.serializer_class.Meta.model.DONE) |
            Q(status=self.serializer_class.Meta.model.CANCELED)
        )[:30]
        if self.request.user.profile.types == Profile.PROFESSIONAL:
            queryset = self.get_queryset().filter(status=self.serializer_class.Meta.model.DONE)[:30]

        return Response(
            self.serializer_class_retrieve(queryset, many=True, context=context).data, status=status.HTTP_200_OK)
