from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import CustomUserViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    r'users', CustomUserViewSet, basename='users'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]
