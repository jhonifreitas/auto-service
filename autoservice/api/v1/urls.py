from django.urls import path
from django.urls import include

from rest_framework import routers

from autoservice.api.v1.auth import views as auth_views
from autoservice.api.v1.core import views as core_views
from autoservice.api.v1.payment import views as payment_views
from autoservice.api.v1.customer import views as customer_views

app_name = 'api.v1'

router = routers.SimpleRouter()
router.register('review', customer_views.ReviewViewSet, basename='review')
router.register('gallery', customer_views.GalleryViewSet, basename='gallery')
router.register('profile/category', customer_views.ProfileCategoryViewSet, basename='profile-category')

urlpatterns = [
    # AUTH
    path('login/', auth_views.LoginViewSet.as_view({'post': 'post'}), name='login'),
    path('register/', customer_views.ProfileViewSet.as_view({'post': 'create'}), name='register'),

    # PAGSEGURO
    path('pagseguro/pay/', payment_views.PaymentViewSet.as_view({'post': 'pay'}), name='pag-pay'),
    path('pagseguro/get-session/', payment_views.PaymentViewSet.as_view({'get': 'get_session'}), name='pag-session'),
    path('pagseguro/notification/', payment_views.PaymentViewSet.as_view({'post': 'notification'}),
         name='pag-notification'),

    # CORE
    path('config/', core_views.ConfigViewSet.as_view({'get': 'retrieve'}), name='config'),
    path('state/', core_views.StateViewSet.as_view({'get': 'list'}), name='state-list'),
    path('city/<int:state_id>/', core_views.CityViewSet.as_view({'get': 'list'}), name='city-list'),
    path('category/', core_views.CategoryViewSet.as_view({'get': 'list'}), name='category-list'),
    path('type-pay/', core_views.TypePayViewSet.as_view({'get': 'list'}), name='type-pay-list'),

    # CUSTOMER
    path('service/<int:service_id>/professional/', customer_views.ProfessionalViewSet.as_view({'get': 'list'}),
         name='professional-list'),
    path('profile/', customer_views.ProfileViewSet.as_view({'patch': 'patch'}), name='profile-update'),
    path('professional/<int:pk>/detail/', customer_views.ProfessionalViewSet.as_view({'get': 'retrieve'}),
         name='professional-detail'),

    path('', include(router.urls)),
]
