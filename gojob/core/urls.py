from django.urls import path

from gojob.core import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
]
