from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from autoservice.api.v1.core import serializers


class StateViewSet(viewsets.ViewSet):

    serializer_class = serializers.StateSerializerRetrieve

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()

    def list(self, request):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)


class CityViewSet(viewsets.ViewSet):

    serializer_class = serializers.CitySerializerRetrieve

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(state_id=self.kwargs.get('state_id'))

    def list(self, request, state_id):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)


class ServiceViewSet(viewsets.ViewSet):

    serializer_class = serializers.ServiceSerializerRetrieve

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()

    def list(self, request):
        context = {'request': request}
        return Response(self.serializer_class(
            self.get_queryset(), many=True, context=context).data, status=status.HTTP_200_OK)


class WeekViewSet(viewsets.ViewSet):

    serializer_class = serializers.WeekSerializerRetrieve

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()

    def list(self, request):
        context = {'request': request}
        return Response(self.serializer_class(
            self.get_queryset(), many=True, context=context).data, status=status.HTTP_200_OK)


class TypePayViewSet(viewsets.ViewSet):

    serializer_class = serializers.TypePaySerializerRetrieve

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()

    def list(self, request):
        context = {'request': request}
        return Response(self.serializer_class(
            self.get_queryset(), many=True, context=context).data, status=status.HTTP_200_OK)
