from django.urls import path
from django.urls import include

from rest_framework import routers

from autoservice.api.v1.auth import views as auth_views
from autoservice.api.v1.core import views as core_views
from autoservice.api.v1.customer import views as customer_views

app_name = 'api.v1'

router = routers.SimpleRouter()
router.register('review', customer_views.ReviewViewSet, basename='review')
router.register('autonomous/service', customer_views.AutonomousServiceViewSet, basename='autonomous-service')

urlpatterns = [
    # AUTH
    path('login/', auth_views.LoginViewSet.as_view({'post': 'post'}), name='login'),
    path('register/autonomous/', customer_views.AutonomousViewSet.as_view({'post': 'create'}),
         name='autonomous-register'),
    path('register/profile/', customer_views.ProfileViewSet.as_view({'post': 'create'}), name='profile-register'),

    # CORE
    path('state/', core_views.StateViewSet.as_view({'get': 'list'}), name='state-list'),
    path('city/<int:state_id>/', core_views.CityViewSet.as_view({'get': 'list'}), name='city-list'),
    path('service/', core_views.ServiceViewSet.as_view({'get': 'list'}), name='service-list'),
    path('week/', core_views.WeekViewSet.as_view({'get': 'list'}), name='week-list'),
    path('type-pay/', core_views.TypePayViewSet.as_view({'get': 'list'}), name='type-pay-list'),

    # CUSTOMER
    path('service/<int:service_id>/autonomous/', customer_views.AutonomousViewSet.as_view({'get': 'list'}),
         name='autonomous-list'),
    path('profile/<int:pk>/', customer_views.ProfileViewSet.as_view({'put': 'update'}), name='profile-update'),
    path('autonomous/<int:pk>/', customer_views.AutonomousViewSet.as_view({'put': 'update'}),
         name='autonomous-update'),
    path('autonomous/<int:pk>/detail/', customer_views.AutonomousViewSet.as_view({'get': 'retrieve'}),
         name='autonomous-detail'),

    path('', include(router.urls)),
]
