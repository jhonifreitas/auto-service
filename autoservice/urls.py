"""autoservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

admin.site.site_header = 'Painel Administrativo'
admin.site.site_title = 'Painel Administrativo'
admin.site.index_title = 'Administração'

urlpatterns = [
    path('', admin.site.urls),

    # PASSWORD RESET
    path('resetar-senha/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('resetar-senha/concluido/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('nova-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('nova-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # API
    path('api/v1/', include('autoservice.api.v1.urls', namespace='api-v1')),

    # HOME
    # path('', include('autoservice.core.urls', namespace='core')),
]

if settings.DEFAULT_FILE_STORAGE == 'django.core.files.storage.FileSystemStorage':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
