from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, GetToken, DeleteToken
from .views import (RecipeViewSet, TagViewSet, IngredientViewSet)

router = DefaultRouter()


router.register('users', UserViewSet, basename='user')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', GetToken.as_view(), name='get_token'),
    path('auth/token/logout/', DeleteToken.as_view(), name='delete_token')
]
