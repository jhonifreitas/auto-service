from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from gojob.api.v1.core import serializers


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


class CategoryViewSet(viewsets.ViewSet):

    serializer_class = serializers.CategorySerializerRetrieve

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


class ConfigViewSet(viewsets.ViewSet):

    serializer_class = serializers.ConfigSerializerRetrieve

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.first()

    def retrieve(self, request):
        return Response(self.serializer_class(self.get_queryset()).data, status=status.HTTP_200_OK)
