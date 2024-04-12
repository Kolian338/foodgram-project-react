from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import CustomUserViewSet, TagViewSet

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    r'users', CustomUserViewSet, basename='users'
)
router_v1.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]
