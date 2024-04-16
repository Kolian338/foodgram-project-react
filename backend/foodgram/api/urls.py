from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    CustomUserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet
)
from django.conf import settings

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    r'users', CustomUserViewSet, basename='users'
)
router_v1.register(
    r'tags', TagViewSet, basename='tags'
)
router_v1.register(
    r'ingredients', IngredientViewSet, basename='ingredients'
)
router_v1.register(
    r'recipes', RecipeViewSet, basename='recipes'
)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
